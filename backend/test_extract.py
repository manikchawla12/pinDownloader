import yt_dlp
import json

url = "https://www.pinterest.com/pin/644929609181853392/"

ydl_opts = {
    'quiet': False,
    # Letting yt-dlp pick
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    try:
        # We don't specify format here to see what the default behavior is
        info = ydl.extract_info(url, download=False)
        print("SUCCESS")
        print(f"Title: {info.get('title')}")
        
        # Check if we have a top-level URL
        direct_url = info.get('url')
        if direct_url:
            print(f"Direct URL found: {direct_url[:100]}...")
        
        # List all formats
        formats = info.get('formats', [])
        print(f"Number of formats found: {len(formats)}")
        for i, f in enumerate(formats):
            print(f"[{i}] ID: {f.get('format_id')}, Ext: {f.get('ext')}, Res: {f.get('resolution')}, URL: {str(f.get('url'))[:50]}...")
            
    except Exception as e:
        print(f"FAILURE: {str(e)}")
