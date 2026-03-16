import asyncio
import re
import logging
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import yt_dlp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Pinterest Video Downloader API")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

def extract_pinterest_video(url: str):
    logger.info(f"Extracting video from URL: {url}")
    ydl_opts = {
        'clean_infojson': True,
        'quiet': True,
        'skip_download': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return info
        except yt_dlp.utils.DownloadError as e:
            logger.error(f"yt-dlp error: {str(e)}")
            raise Exception(f"Failed to extract video: {str(e)}")

def is_valid_pinterest_url(url: str) -> bool:
    """Validate that the URL belongs to Pinterest."""
    pattern = r'^https?://([a-zA-Z0-9-]+\.)?(pinterest\.[a-z]{2,}(\.[a-z]{2})?|pin\.it)/.*$'
    return bool(re.match(pattern, url))

@app.get("/api/download")
@limiter.limit("15/minute")
async def download_video(request: Request, url: str = Query(..., description="Pinterest Video URL to download")):
    if not is_valid_pinterest_url(url):
        raise HTTPException(status_code=400, detail="Invalid Pinterest URL provided.")
    
    try:
        info = await asyncio.to_thread(extract_pinterest_video, url)
        
        # Robust extraction logic
        video_url = None
        
        # 1. Best quality format
        formats = info.get('formats', [])
        video_formats = [f for f in formats if f.get('vcodec') != 'none' and f.get('ext') == 'mp4']
        if video_formats:
            # Sort by width/height to get best quality
            video_formats.sort(key=lambda x: (x.get('width', 0) or 0) * (x.get('height', 0) or 0), reverse=True)
            video_url = video_formats[0].get('url')
            
        # 2. Fallback to top-level url
        if not video_url:
            video_url = info.get('url')
            
        # 3. Last fallback
        if not video_url and formats:
            video_url = formats[-1].get('url')

        thumbnail = info.get('thumbnail')
        title = info.get('title', 'Pinterest Video')
        
        if not video_url:
            logger.warning(f"No video found for URL: {url}")
            raise HTTPException(status_code=404, detail="No playable video found at this URL.")
            
        logger.info(f"Successfully extracted: {title}")
        return {
            "success": True,
            "title": title,
            "video_url": video_url,
            "thumbnail": thumbnail
        }
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/p")
@app.get("/api/p")
async def proxy_download(url: str = Query(..., description="Direct video URL to proxy"), 
                         filename: str = Query("video.mp4", description="Filename for the downloaded file")):
    logger.info(f"Proxying download: {filename}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.pinterest.com/"
    }
    
    client = httpx.AsyncClient(follow_redirects=True, timeout=60.0)
    
    try:
        request = client.build_request("GET", url, headers=headers)
        response = await client.send(request, stream=True)
        
        if response.status_code >= 400:
            logger.error(f"Pinterest proxy error {response.status_code}: {response.reason_phrase}")
            await response.aclose()
            await client.aclose()
            raise HTTPException(status_code=response.status_code, detail=f"Source error: {response.reason_phrase}")

        async def stream_video():
            try:
                async for chunk in response.aiter_bytes():
                    yield chunk
            finally:
                await response.aclose()
                await client.aclose()

        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
        
        content_length = response.headers.get("Content-Length")
        if content_length:
            headers["Content-Length"] = content_length

        return StreamingResponse(stream_video(), media_type="video/mp4", headers=headers)
        
    except Exception as e:
        logger.error(f"Proxy Error: {str(e)}")
        if 'client' in locals():
            await client.aclose()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "alive", "version": "1.0.8", "timestamp": "2026-03-16T19:33"}

@app.get("/api/routes")
async def list_routes():
    return [{"path": route.path} for route in app.routes]
