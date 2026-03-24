from __future__ import annotations
import asyncio
import re
import os
import json
import uuid
import logging
import tempfile
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, Query, Depends, Body
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import yt_dlp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ──────────────────────── App Setup ────────────────────────

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Pinterest Video Downloader API")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ──────────────────────── Admin Auth ────────────────────────
# REQUIRED: Set these via environment variables. No defaults for security.
ADMIN_USERNAME = (os.environ.get("ADMIN_USERNAME") or "").strip()
ADMIN_PASSWORD = (os.environ.get("ADMIN_PASSWORD") or "").strip()
SECRET_KEY = (os.environ.get("SECRET_KEY") or "").strip()

if not all([ADMIN_USERNAME, ADMIN_PASSWORD, SECRET_KEY]):
    logger.warning(
        "⚠️  ADMIN_USERNAME, ADMIN_PASSWORD, or SECRET_KEY env vars are not set. "
        "Admin login will be disabled until they are configured."
    )
else:
    logger.info(f"Admin auth configured for user: '{ADMIN_USERNAME}' (password length: {len(ADMIN_PASSWORD)}, key length: {len(SECRET_KEY)})")

# Simple in-memory token store (survives as long as the process is up)
active_tokens: dict[str, datetime] = {}
TOKEN_EXPIRY_HOURS = 24

def generate_token(username: str) -> str:
    """Generate a simple token from username + timestamp + secret."""
    raw = f"{username}:{datetime.utcnow().isoformat()}:{SECRET_KEY}"
    token = hashlib.sha256(raw.encode()).hexdigest()
    active_tokens[token] = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)
    return token

def verify_token(token: str) -> bool:
    """Verify a token is valid and not expired."""
    if token not in active_tokens:
        return False
    if datetime.utcnow() > active_tokens[token]:
        del active_tokens[token]
        return False
    return True

async def get_admin_user(request: Request):
    """Dependency: extract and verify admin token from Authorization header."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = auth.replace("Bearer ", "")
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return True

# ──────────────────────── Blog Storage ────────────────────────

BLOG_DATA_DIR = Path(os.environ.get("BLOG_DATA_DIR", "./data/blog"))
BLOG_DATA_DIR.mkdir(parents=True, exist_ok=True)
BLOG_INDEX_FILE = BLOG_DATA_DIR / "index.json"

def _load_blog_index() -> list[dict]:
    if BLOG_INDEX_FILE.exists():
        with open(BLOG_INDEX_FILE, "r") as f:
            return json.load(f)
    return []

def _save_blog_index(posts: list[dict]):
    with open(BLOG_INDEX_FILE, "w") as f:
        json.dump(posts, f, indent=2, default=str)

def _load_blog_post(slug: str) -> Optional[dict]:
    post_file = BLOG_DATA_DIR / f"{slug}.json"
    if post_file.exists():
        with open(post_file, "r") as f:
            return json.load(f)
    return None

def _save_blog_post(post: dict):
    slug = post["slug"]
    post_file = BLOG_DATA_DIR / f"{slug}.json"
    with open(post_file, "w") as f:
        json.dump(post, f, indent=2, default=str)

# ──────────────────────── yt-dlp helpers ────────────────────────

def extract_pinterest_video(url: str):
    """Extract metadata only (no download)."""
    logger.info(f"Extracting video from URL: {url}")
    ydl_opts = {
        'clean_infojson': True,
        'quiet': True,
        'skip_download': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'socket_timeout': 30,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            logger.info(f"Available formats: {len(formats)}")
            return info
        except yt_dlp.utils.DownloadError as e:
            logger.error(f"yt-dlp error: {str(e)}")
            raise Exception(f"Failed to extract video: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during extraction: {str(e)}", exc_info=True)
            raise Exception(f"Failed to extract video: {str(e)}")


def download_video_to_file(url: str, output_path: str):
    """Download the video to a temp file using yt-dlp as a library.
    This handles HLS merging, cookies, retries, and signatures correctly.
    
    Pinterest serves split video+audio HLS segments. If ffmpeg is available
    we merge them; otherwise we download the best single-stream format.
    """
    import shutil
    has_ffmpeg = shutil.which("ffmpeg") is not None
    
    logger.info(f"Downloading video to {output_path} (ffmpeg={'yes' if has_ffmpeg else 'no'})")
    
    base_opts = {
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'socket_timeout': 30,
        'retries': 3,
        'fragment_retries': 3,
    }
    
    if has_ffmpeg:
        # Ideal: merge best video + best audio into MP4
        base_opts['format'] = 'bestvideo*+bestaudio/bestvideo*/best'
        base_opts['merge_output_format'] = 'mp4'
    else:
        # Fallback: pick the single best-quality stream (video-only is fine)
        base_opts['format'] = 'bestvideo*/best'
    
    with yt_dlp.YoutubeDL(base_opts) as ydl:
        ydl.download([url])
    logger.info(f"Download complete: {output_path}, size={os.path.getsize(output_path)} bytes")


def is_valid_pinterest_url(url: str) -> bool:
    """Validate that the URL belongs to Pinterest."""
    pattern = r'^https?://([a-zA-Z0-9-]+\.)?(pinterest\.[a-z]{2,}(\.[a-z]{2})?|pin\.it)/.*$'
    return bool(re.match(pattern, url))

# ──────────────────────── Keep-Alive / Warm-up ────────────────────────

@app.on_event("startup")
async def startup_warm():
    """Pre-warm yt-dlp import on startup to reduce first-request latency."""
    logger.info("Pre-warming yt-dlp...")
    # Just accessing the module ensures it's loaded in memory
    _ = yt_dlp.version.__version__
    logger.info(f"yt-dlp version {_} loaded and warm.")
    # Start the self-ping background task
    asyncio.create_task(self_ping_loop())

async def self_ping_loop():
    """Ping /health every 5 minutes to prevent Render from sleeping."""
    import httpx
    render_url = os.environ.get("RENDER_EXTERNAL_URL")
    if not render_url:
        logger.info("RENDER_EXTERNAL_URL not set — self-ping disabled (local dev).")
        return
    
    health_url = f"{render_url}/health"
    logger.info(f"Self-ping enabled: will ping {health_url} every 5 min.")
    
    async with httpx.AsyncClient() as client:
        while True:
            await asyncio.sleep(300)  # 5 minutes
            try:
                resp = await client.get(health_url, timeout=10)
                logger.info(f"Self-ping OK: {resp.status_code}")
            except Exception as e:
                logger.warning(f"Self-ping failed: {e}")

# ──────────────────────── Video API ────────────────────────

@app.get("/api/info")
@limiter.limit("15/minute")
async def get_video_info(request: Request, url: str = Query(..., description="Pinterest Video URL to fetch info")):
    if not is_valid_pinterest_url(url):
        raise HTTPException(status_code=400, detail="Invalid Pinterest URL provided.")
    
    try:
        info = await asyncio.to_thread(extract_pinterest_video, url)
        
        thumbnail = info.get('thumbnail')
        title = info.get('title', 'Pinterest Video')
        
        if not info.get('formats') and not info.get('url'):
            raise HTTPException(status_code=404, detail="No video found at this URL.")
            
        return {
            "success": True,
            "title": title,
            "thumbnail": thumbnail,
            "duration": info.get('duration'),
            "original_url": url
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Info API Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/download")
@limiter.limit("10/minute")
async def download_video(request: Request,
                         url: str = Query(..., description="Pinterest Pin URL to download"),
                         filename: str = Query("video.mp4", description="Filename for the download")):
    """
    Downloads the video using yt-dlp as a library (in-process).
    This handles cookies, HLS merging, retries, and signatures properly.
    The video is downloaded to a temp file first, then streamed to the user.
    """
    if not is_valid_pinterest_url(url):
        raise HTTPException(status_code=400, detail="Invalid Pinterest URL provided.")

    logger.info(f"Download requested for: {url}")
    
    # Create a temp file for the download
    tmp_dir = tempfile.mkdtemp(prefix="pinclip_")
    output_path = os.path.join(tmp_dir, "video.mp4")
    
    try:
        # Download the video using yt-dlp library (not subprocess)
        await asyncio.to_thread(download_video_to_file, url, output_path)
        
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            raise HTTPException(status_code=500, detail="Download produced an empty file.")
        
        file_size = os.path.getsize(output_path)
        logger.info(f"Serving {file_size} bytes as {filename}")
        
        async def stream_file():
            try:
                with open(output_path, "rb") as f:
                    while True:
                        chunk = f.read(1024 * 64)  # 64KB chunks
                        if not chunk:
                            break
                        yield chunk
            finally:
                # Clean up temp files
                try:
                    os.remove(output_path)
                    os.rmdir(tmp_dir)
                except Exception:
                    pass
        
        response_headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "video/mp4",
            "Content-Length": str(file_size),
            "Access-Control-Expose-Headers": "Content-Disposition, Content-Length",
        }
        
        return StreamingResponse(stream_file(), headers=response_headers)

    except HTTPException:
        raise
    except Exception as e:
        # Clean up on error too
        try:
            if os.path.exists(output_path):
                os.remove(output_path)
            os.rmdir(tmp_dir)
        except Exception:
            pass
        logger.error(f"Download Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


# ──────────────────────── Auth API ────────────────────────

@app.post("/api/admin/login")
@limiter.limit("5/minute")
async def admin_login(request: Request):
    if not all([ADMIN_USERNAME, ADMIN_PASSWORD, SECRET_KEY]):
        raise HTTPException(status_code=503, detail="Admin auth is not configured. Set ADMIN_USERNAME, ADMIN_PASSWORD, and SECRET_KEY env vars.")
    
    body = await request.json()
    username = body.get("username", "").strip()
    password = body.get("password", "").strip()
    
    logger.info(f"Login attempt: user='{username}' (expected='{ADMIN_USERNAME}'), pass_len={len(password)} (expected_len={len(ADMIN_PASSWORD)})")
    
    if username != ADMIN_USERNAME or password != ADMIN_PASSWORD:
        logger.warning(f"Login failed: username_match={username == ADMIN_USERNAME}, password_match={password == ADMIN_PASSWORD}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = generate_token(username)
    logger.info(f"Admin login successful for: {username}")
    return {"token": token, "expires_in": TOKEN_EXPIRY_HOURS * 3600}


@app.get("/api/admin/verify")
async def verify_admin(is_admin: bool = Depends(get_admin_user)):
    return {"valid": True}


# ──────────────────────── Blog API ────────────────────────

@app.get("/api/blog")
async def list_blog_posts():
    """Public: List all published blog posts."""
    posts = _load_blog_index()
    # Return only published posts, newest first
    published = [p for p in posts if p.get("published", True)]
    published.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return {"posts": published}


@app.get("/api/blog/{slug}")
async def get_blog_post(slug: str):
    """Public: Get a single blog post by slug."""
    post = _load_blog_post(slug)
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    return post


@app.post("/api/admin/blog")
@limiter.limit("10/minute")
async def create_blog_post(request: Request, is_admin: bool = Depends(get_admin_user)):
    """Admin: Create a new blog post."""
    body = await request.json()
    
    title = body.get("title", "").strip()
    content = body.get("content", "").strip()
    excerpt = body.get("excerpt", "").strip()
    cover_image = body.get("cover_image", "")
    published = body.get("published", True)
    
    if not title or not content:
        raise HTTPException(status_code=400, detail="Title and content are required")
    
    # Generate slug from title
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    
    # Ensure unique slug
    existing = _load_blog_index()
    existing_slugs = {p["slug"] for p in existing}
    base_slug = slug
    counter = 1
    while slug in existing_slugs:
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    now = datetime.utcnow().isoformat()
    post = {
        "slug": slug,
        "title": title,
        "content": content,
        "excerpt": excerpt or content[:200] + "...",
        "cover_image": cover_image,
        "published": published,
        "created_at": now,
        "updated_at": now,
    }
    
    # Save full post
    _save_blog_post(post)
    
    # Update index
    index_entry = {k: v for k, v in post.items() if k != "content"}
    existing.append(index_entry)
    _save_blog_index(existing)
    
    logger.info(f"Blog post created: {slug}")
    return {"success": True, "slug": slug, "post": post}


@app.put("/api/admin/blog/{slug}")
@limiter.limit("10/minute")
async def update_blog_post(slug: str, request: Request, is_admin: bool = Depends(get_admin_user)):
    """Admin: Update an existing blog post."""
    existing_post = _load_blog_post(slug)
    if not existing_post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    body = await request.json()
    
    # Update fields
    if "title" in body:
        existing_post["title"] = body["title"].strip()
    if "content" in body:
        existing_post["content"] = body["content"].strip()
    if "excerpt" in body:
        existing_post["excerpt"] = body["excerpt"].strip()
    if "cover_image" in body:
        existing_post["cover_image"] = body["cover_image"]
    if "published" in body:
        existing_post["published"] = body["published"]
    
    existing_post["updated_at"] = datetime.utcnow().isoformat()
    
    _save_blog_post(existing_post)
    
    # Update index
    index = _load_blog_index()
    for i, p in enumerate(index):
        if p["slug"] == slug:
            index[i] = {k: v for k, v in existing_post.items() if k != "content"}
            break
    _save_blog_index(index)
    
    logger.info(f"Blog post updated: {slug}")
    return {"success": True, "post": existing_post}


@app.delete("/api/admin/blog/{slug}")
async def delete_blog_post(slug: str, is_admin: bool = Depends(get_admin_user)):
    """Admin: Delete a blog post."""
    post_file = BLOG_DATA_DIR / f"{slug}.json"
    if not post_file.exists():
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    post_file.unlink()
    
    # Remove from index
    index = _load_blog_index()
    index = [p for p in index if p["slug"] != slug]
    _save_blog_index(index)
    
    logger.info(f"Blog post deleted: {slug}")
    return {"success": True}


@app.get("/api/admin/blog")
async def admin_list_blog_posts(is_admin: bool = Depends(get_admin_user)):
    """Admin: List ALL blog posts (including unpublished)."""
    posts = _load_blog_index()
    posts.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return {"posts": posts}


# ──────────────────────── Health & Routes ────────────────────────

@app.get("/health")
async def health_check():
    return {"status": "alive", "version": "2.0.0", "timestamp": "2026-03-24T10:30"}

@app.get("/api/routes")
async def list_routes():
    return [{"path": route.path, "methods": list(getattr(route, 'methods', []))} for route in app.routes]
