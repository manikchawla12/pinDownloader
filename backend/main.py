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

@app.get("/api/download")
@limiter.limit("15/minute")
async def download_video(request: Request, url: str = Query(..., description="Pinterest Video URL to download")):
    if not is_valid_pinterest_url(url):
        raise HTTPException(status_code=400, detail="Invalid Pinterest URL provided.")
    
    try:
        info = await asyncio.to_thread(extract_pinterest_video, url)
        
        # Robust extraction logic
        video_url = None
        video_size = None

        formats = info.get('formats', [])
        logger.info(f"Analyzing {len(formats)} total formats...")

        # Only filter out m3u8 playlists (true HLS playlists)
        # V_HLSV4-* formats are HLS video segments with actual downloadable URLs - these are valid!
        true_hls_playlists = [f for f in formats if f.get('ext') == 'm3u8']
        usable_formats = [f for f in formats if f.get('ext') != 'm3u8']

        logger.info(f"Found {len(usable_formats)} usable formats, {len(true_hls_playlists)} m3u8 playlists")

        # If only m3u8 playlists available with no downloadable segments, error
        if not usable_formats and true_hls_playlists:
            logger.error("Only m3u8 playlists available with no downloadable segments.")
            raise HTTPException(status_code=400, detail="This video only offers HLS streaming format without direct download capability.")

        # Priority 1: MP4 with both video and audio codecs
        video_audio_formats = [f for f in usable_formats if
                                f.get('vcodec') not in (None, 'none') and
                                f.get('acodec') not in (None, 'none') and
                                f.get('ext') == 'mp4']
        logger.info(f"Found {len(video_audio_formats)} MP4 formats with video+audio")

        if video_audio_formats:
            # Sort by quality (height first, then width)
            video_audio_formats.sort(key=lambda x: (
                x.get('height') or 0,
                x.get('width') or 0
            ), reverse=True)
            selected = video_audio_formats[0]
            video_url = selected.get('url')
            video_size = selected.get('filesize') or selected.get('filesize_approx')
            logger.info(f"Selected MP4 with audio: {selected.get('format_id')} (size: {video_size}, h: {selected.get('height')}, w: {selected.get('width')})")

        # Priority 2: MP4 with video codec only (from HLS segments - V_HLSV4-*)
        if not video_url:
            video_only_formats = [f for f in usable_formats if
                                   f.get('vcodec') not in (None, 'none') and
                                   f.get('ext') == 'mp4']
            logger.info(f"Found {len(video_only_formats)} MP4 video-only formats (includes HLS segments)")

            if video_only_formats:
                # Sort by quality
                video_only_formats.sort(key=lambda x: (
                    x.get('height') or 0,
                    x.get('width') or 0
                ), reverse=True)
                selected = video_only_formats[0]
                video_url = selected.get('url')
                video_size = selected.get('filesize') or selected.get('filesize_approx')
                logger.info(f"Selected MP4 video-only: {selected.get('format_id')} (size: {video_size}, h: {selected.get('height')}, w: {selected.get('width')})")

        # Priority 3: Any format with video codec
        if not video_url:
            logger.info("No MP4 video format found, trying other video formats...")
            other_video_formats = [f for f in usable_formats if f.get('vcodec') not in (None, 'none')]

            if other_video_formats:
                other_video_formats.sort(key=lambda x: (
                    x.get('height') or 0,
                    x.get('width') or 0
                ), reverse=True)
                selected = other_video_formats[0]
                video_url = selected.get('url')
                video_size = selected.get('filesize') or selected.get('filesize_approx')
                logger.info(f"Selected {selected.get('ext')}: {selected.get('format_id')} (size: {video_size}, h: {selected.get('height')})")

        # Priority 4: Fallback to any available format with URL
        if not video_url:
            logger.info("No video codec found, trying best quality format by height...")
            formats_with_url = [f for f in usable_formats if f.get('url')]

            if formats_with_url:
                formats_with_url.sort(key=lambda x: (
                    x.get('height') or 0,
                    x.get('width') or 0
                ), reverse=True)
                selected = formats_with_url[0]
                video_url = selected.get('url')
                video_size = selected.get('filesize') or selected.get('filesize_approx')
                logger.info(f"Selected best available: {selected.get('format_id')} (ext: {selected.get('ext')}, size: {video_size})")

        # Priority 5: Use the top-level url from info dict
        if not video_url:
            video_url = info.get('url')
            if video_url:
                logger.info("Using top-level URL from info dict as fallback")

        thumbnail = info.get('thumbnail')
        title = info.get('title', 'Pinterest Video')
        
        if not video_url:
            logger.error(f"No suitable video URL found for: {url}")
            logger.error(f"Usable formats: {len(usable_formats)}, m3u8 playlists: {len(true_hls_playlists)}")
            logger.debug(f"All format IDs: {[f.get('format_id') for f in formats]}")
            raise HTTPException(status_code=404, detail="No playable video found at this URL.")
            
        logger.info(f"Successfully extracted: {title} (size: {video_size} bytes, URL: {video_url[:100]}...)")
        return {
            "success": True,
            "title": title,
            "video_url": video_url,
            "thumbnail": thumbnail,
            "size": video_size
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/p")
@app.get("/api/p")
async def proxy_download(url: str = Query(..., description="Direct video URL to proxy"), 
                         filename: str = Query("video.mp4", description="Filename for the downloaded file")):
    logger.info(f"Proxying download: {filename} from URL: {url[:100]}...")

    # Reject M3U8 playlists - they need special handling
    if '.m3u8' in url.lower() or 'application/vnd.apple.mpegurl' in url.lower():
        logger.error(f"M3U8 playlist detected: {url[:100]}. This requires HLS processing.")
        raise HTTPException(status_code=400, detail="M3U8 HLS playlists are not supported. Please provide a direct video URL.")

    request_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.pinterest.com/",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Sec-Fetch-Dest": "video",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
    }
    
    client = httpx.AsyncClient(follow_redirects=True, timeout=120.0)

    try:
        logger.info(f"Building request with headers: {list(request_headers.keys())}")
        http_request = client.build_request("GET", url, headers=request_headers)
        response = await client.send(http_request, stream=True)

        logger.info(f"Response status: {response.status_code}, Content-Length: {response.headers.get('Content-Length', 'unknown')}")

        if response.status_code >= 400:
            # Try to read error response for debugging
            error_body = await response.aread()
            logger.error(f"Pinterest proxy error {response.status_code}: {response.reason_phrase}, Body: {error_body[:500]}")
            await response.aclose()
            await client.aclose()
            raise HTTPException(status_code=response.status_code, detail=f"Source error: {response.reason_phrase}")

        # Verify we have actual video content
        content_length = response.headers.get("Content-Length")
        if content_length:
            try:
                cl_int = int(content_length)
                if cl_int < 10000:  # Less than 10KB is suspicious for a video
                    logger.warning(f"Suspicious content length: {cl_int} bytes. This might be an error page or playlist.")
                    # Check if it's an M3U8 despite not having .m3u8 in URL
                    await response.aclose()
                    await client.aclose()
                    raise HTTPException(status_code=400, detail="Content appears to be a playlist, not a direct video file. Try extracting the video again.")
            except ValueError:
                pass

        content_type = response.headers.get("Content-Type", "")
        logger.info(f"Response Content-Type: {content_type}")

        # Reject HLS/playlist content types
        if content_type and ("mpegurl" in content_type.lower() or "vnd.apple" in content_type.lower()):
            logger.error(f"M3U8 playlist detected by content-type: {content_type}")
            await response.aclose()
            await client.aclose()
            raise HTTPException(status_code=400, detail="M3U8 HLS playlists are not supported. Please try extracting the video again.")

        # Warn if content type doesn't look like video
        if content_type and "video" not in content_type.lower() and "octet-stream" not in content_type.lower():
            logger.warning(f"Unexpected Content-Type: {content_type}")

        async def stream_video():
            bytes_streamed = 0
            try:
                async for chunk in response.aiter_bytes(chunk_size=8192):
                    bytes_streamed += len(chunk)
                    yield chunk
                logger.info(f"Successfully streamed {bytes_streamed} bytes")
            except Exception as e:
                logger.error(f"Error during streaming: {str(e)}")
                raise
            finally:
                await response.aclose()
                await client.aclose()

        response_headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "Access-Control-Expose-Headers": "Content-Disposition",
        }
        
        if content_length:
            response_headers["Content-Length"] = content_length

        return StreamingResponse(stream_video(), media_type="video/mp4", headers=response_headers)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Proxy Error: {str(e)}", exc_info=True)
        if 'client' in locals():
            await client.aclose()
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "alive", "version": "1.0.8", "timestamp": "2026-03-16T19:33"}

@app.get("/api/routes")
async def list_routes():
    return [{"path": route.path} for route in app.routes]
