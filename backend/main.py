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
            raise Exception(f"Failed to extract video: {str(e)}")

def is_valid_pinterest_url(url: str) -> bool:
    """Validate that the URL belongs to Pinterest (including various TLDs)."""
    # Matches pinterest.com, pinterest.ca, pinterest.co.uk, etc. and pin.it
    pattern = r'^https?://([a-zA-Z0-9-]+\.)?(pinterest\.[a-z]{2,}(\.[a-z]{2})?|pin\.it)/.*$'
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
        
        # Try to find the best MP4 format first
        video_url = None
        formats = info.get('formats', [])
        
        # Look for mp4 formats with video and audio
        mp4_formats = [f for f in formats if f.get('ext') == 'mp4' and f.get('vcodec') != 'none']
        if mp4_formats:
            # Sort by quality (usually width/height) if available
            mp4_formats.sort(key=lambda x: (x.get('width', 0) or 0) * (x.get('height', 0) or 0), reverse=True)
            video_url = mp4_formats[0].get('url')
        
        # Fallback to top-level url if it's an mp4
        if not video_url:
            top_level_url = info.get('url')
            if top_level_url and ('.mp4' in top_level_url or 'video' in top_level_url):
                video_url = top_level_url

        # Last resort: just take any video format
        if not video_url and formats:
            video_formats = [f for f in formats if f.get('vcodec') != 'none']
            if video_formats:
                video_url = video_formats[-1].get('url')

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
    Proxies the download of the video file to bypass Pinterest constraints and ensure a direct download experience.
    """
    async def stream_video():
        async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as client:
            async with client.stream("GET", url) as response:
                if response.status_code >= 400:
                    yield b"Error: Could not fetch video from source."
                    return
                
                async for chunk in response.aiter_bytes():
                    yield chunk

    # We need to know the content type if possible, or default to video/mp4
    return StreamingResponse(
        stream_video(),
        media_type="video/mp4",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache"
        }
    )

@app.get("/health")
async def health_check():
    """Health check endpoint for Render deployment."""
    return {"status": "ok", "version": "1.0.3", "note": "DIAGNOSTIC_VERSION"}

@app.get("/api/v2/test")
async def test_route_v2():
    return {"message": "V2 API is working", "timestamp": "2026-03-16"}

