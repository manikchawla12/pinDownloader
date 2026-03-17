import asyncio
from asyncio import subprocess
import re
import logging
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
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
        'quiet': False,
        'skip_download': True,
        'no_warnings': False,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'socket_timeout': 30,
        'extractor_args': {'youtube': {'player_client': ['web']}},
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)

            # Log detailed format information
            formats = info.get('formats', [])
            logger.info(f"Available formats: {len(formats)}")
            for i, fmt in enumerate(formats[:10]):  # Log first 10 formats
                logger.info(f"Format {i}: id={fmt.get('format_id')}, ext={fmt.get('ext')}, vcodec={fmt.get('vcodec')}, acodec={fmt.get('acodec')}, size={fmt.get('filesize', 'unknown')}, h={fmt.get('height')}, w={fmt.get('width')}")

            return info
        except yt_dlp.utils.DownloadError as e:
            logger.error(f"yt-dlp error: {str(e)}")
            raise Exception(f"Failed to extract video: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during extraction: {str(e)}", exc_info=True)
            raise Exception(f"Failed to extract video: {str(e)}")

def is_valid_pinterest_url(url: str) -> bool:
    """Validate that the URL belongs to Pinterest."""
    pattern = r'^https?://([a-zA-Z0-9-]+\.)?(pinterest\.[a-z]{2,}(\.[a-z]{2})?|pin\.it)/.*$'
    return bool(re.match(pattern, url))

@app.get("/api/info")
@limiter.limit("15/minute")
async def get_video_info(request: Request, url: str = Query(..., description="Pinterest Video URL to fetch info")):
    if not is_valid_pinterest_url(url):
        raise HTTPException(status_code=400, detail="Invalid Pinterest URL provided.")
    
    try:
        info = await asyncio.to_thread(extract_pinterest_video, url)
        
        thumbnail = info.get('thumbnail')
        title = info.get('title', 'Pinterest Video')
        
        # We still check if a video exists conceptually
        if not info.get('formats') and not info.get('url'):
            raise HTTPException(status_code=404, detail="No video found at this URL.")
            
        return {
            "success": True,
            "title": title,
            "thumbnail": thumbnail,
            "duration": info.get('duration'),
            "original_url": url
        }
    except Exception as e:
        logger.error(f"Info API Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download")
@limiter.limit("10/minute")
async def stream_video(request: Request,
                       url: str = Query(..., description="Pinterest Pin URL to download"),
                       filename: str = Query("video.mp4", description="Filename for the download")):
    """
    BEST: Let yt-dlp handle the download directly.
    This handles cookies, HLS merging, retries, and signatures robustly.
    """
    if not is_valid_pinterest_url(url):
        raise HTTPException(status_code=400, detail="Invalid Pinterest URL provided.")

    logger.info(f"Streaming download requested for: {url}")
    
    cmd = [
        "python3", "-m", "yt_dlp",
        url,
        "-o", "-", # Output to stdout
        "--quiet",
        "--no-warnings",
        "--format", "best", # Let yt-dlp pick the absolute best format
        "--merge-output-format", "mp4",
        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        async def stream_output():
            try:
                if process.stdout:
                    while True:
                        chunk = await process.stdout.read(1024 * 64)
                        if not chunk:
                            break
                        yield chunk
            except Exception as e:
                logger.error(f"Error streaming from yt-dlp: {e}")
            finally:
                if process.returncode is None:
                    try:
                        process.terminate()
                    except:
                        pass
                await process.wait()

        response_headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "video/mp4",
            "Access-Control-Expose-Headers": "Content-Disposition",
        }
        
        return StreamingResponse(stream_output(), headers=response_headers)

    except Exception as e:
        logger.error(f"Streaming Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

# Removed proxy and previous reliable endpoints in favor of consolidated /api/download

@app.get("/health")
async def health_check():
    return {"status": "alive", "version": "1.0.8", "timestamp": "2026-03-16T19:33"}

@app.get("/api/routes")
async def list_routes():
    return [{"path": route.path} for route in app.routes]
