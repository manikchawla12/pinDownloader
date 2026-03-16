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

@app.get("/health")
async def health_check():
    """Health check endpoint with versioning."""
    return {"status": "alive", "version": "1.0.6", "timestamp": "2026-03-16T19:12"}

@app.get("/api/routes")
async def list_routes():
    """List all available routes for debugging."""
    return [{"path": route.path} for route in app.routes]

@app.get("/api/p")
@app.get("/p")
async def proxy_download(url: str = Query(..., description="Direct video URL to proxy"), 
                         filename: str = Query("video.mp4", description="Filename for the downloaded file")):
    """
    Proxies the video download to bypass Pinterest's direct link protections.
    Now with proper error handling and Content-Length support.
    """
    # Use a specific User-Agent to avoid being blocked by CDNs
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.pinterest.com/"
    }
    
    client = httpx.AsyncClient(follow_redirects=True, timeout=60.0)
    
    try:
        # Build the request
        request = client.build_request("GET", url, headers=headers)
        # Send it but stream the response
        response = await client.send(request, stream=True)
        
        if response.status_code >= 400:
            await response.aclose()
            await client.aclose()
            raise HTTPException(status_code=response.status_code, detail=f"Failed to fetch video: {response.reason_phrase}")

        async def stream_video():
            try:
                async for chunk in response.aiter_bytes():
                    yield chunk
            finally:
                await response.aclose()
                await client.aclose()

        # Extract headers for the proxy response
        proxy_headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
        
        # Add Content-Length if available from the source
        content_length = response.headers.get("Content-Length")
        if content_length:
            proxy_headers["Content-Length"] = content_length

        return StreamingResponse(
            stream_video(),
            media_type="video/mp4",
            headers=proxy_headers
        )
        
    except Exception as e:
        if 'client' in locals():
            await client.aclose()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v2/test")
async def test_route_v2():
    return {"message": "V2 API is working", "timestamp": "2026-03-16"}



