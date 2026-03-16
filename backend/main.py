import asyncio
import re
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import yt_dlp

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Pinterest Video Downloader API")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
# In production, you would restrict allow_origins to your Vercel frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

def extract_pinterest_video(url: str):
    ydl_opts = {
        'clean_infojson': False,
        'quiet': True,
        'skip_download': True,
        'format': 'best',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return info
        except yt_dlp.utils.DownloadError as e:
            raise Exception(f"Failed to extract video: {str(e)}")

def is_valid_pinterest_url(url: str) -> bool:
    """Validate that the URL belongs to Pinterest."""
    pattern = r'^https?://([a-zA-Z0-9-]+\.)?(pinterest\.com|pin\.it)/.*$'
    return bool(re.match(pattern, url))

@app.get("/api/download")
@limiter.limit("15/minute")
async def download_video(request: Request, url: str = Query(..., description="Pinterest Video URL to download")):
    """
    Extracts the direct MP4 URL and metadata from a given Pinterest video URL.
    """
    if not is_valid_pinterest_url(url):
        raise HTTPException(status_code=400, detail="Invalid Pinterest URL provided.")
    
    try:
        # Run the synchronous yt-dlp extraction in a separate thread to avoid blocking the event loop
        info = await asyncio.to_thread(extract_pinterest_video, url)
        
        video_url = info.get('url')
        thumbnail = info.get('thumbnail')
        title = info.get('title', 'Pinterest Video')
        
        if not video_url:
            raise HTTPException(status_code=404, detail="No playable video found at this URL. Please ensure it is a video pin.")
            
        return {
            "success": True,
            "title": title,
            "video_url": video_url,
            "thumbnail": thumbnail
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/proxy-download")
async def proxy_download(url: str = Query(..., description="Direct video URL to proxy"), 
                         filename: str = Query("video.mp4", description="Filename for the downloaded file")):
    """
    DEBUG: Testing if this endpoint is even reachable.
    """
    return {"message": "Proxy endpoint reached", "url": url, "filename": filename}

@app.get("/health")
async def health_check():
    """Health check endpoint for Render deployment."""
    return {"status": "ok", "version": "1.0.2", "note": "Routing test"}

@app.get("/api/test")
async def test_route():
    return {"message": "API is responding correctly"}
