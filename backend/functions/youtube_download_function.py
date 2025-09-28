import os
import requests
from io import BytesIO
from PIL import Image
import yt_dlp
import logging

logger = logging.getLogger(__name__)

def process_youtube_video(video_url, video_output_dir=None, thumbnail_size=(320, 180),
                          serial=None, thumbnail_output_dir=None):
    if not os.path.exists(video_output_dir):
        os.makedirs(video_output_dir)
    if not os.path.exists(thumbnail_output_dir):
        os.makedirs(thumbnail_output_dir)

    ydl_opts = {
        'outtmpl': os.path.join(video_output_dir, f'{serial}.%(ext)s'),
        'format': 'bestvideo[height=1080]+bestaudio/best[height=1080]/best',
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
        'http_headers': {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/115.0 Safari/537.36'
            ),
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
    except Exception as e:
        logger.error(f"yt-dlp failed to download video: {video_url} | Error: {e}")
        raise

    title = info_dict.get('title', 'Unknown Title')
    description = info_dict.get('description', 'No Description')
    thumbnail_url = info_dict.get('thumbnail', '')

    thumbnail_path = None
    if thumbnail_url:
        try:
            response = requests.get(thumbnail_url)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            img = img.resize(thumbnail_size, Image.LANCZOS)
            thumbnail_path = os.path.join(thumbnail_output_dir, f"{serial}.jpg")
            img.save(thumbnail_path, "JPEG")
        except Exception as e:
            logger.warning(f"Failed to download/resize thumbnail for {video_url}: {e}")

    return title, description, thumbnail_url, thumbnail_path
