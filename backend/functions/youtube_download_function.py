import yt_dlp
import os
from PIL import Image
import requests
from io import BytesIO

def process_youtube_video(video_url, video_output_dir=None, thumbnail_size=(320, 180), serial=None, thumbnail_output_dir=None):
    if not os.path.exists(video_output_dir):
        os.makedirs(video_output_dir)
    if not os.path.exists(thumbnail_output_dir):
        os.makedirs(thumbnail_output_dir)

    ydl_opts = {
        'outtmpl': os.path.join(video_output_dir, f'{serial}.%(ext)s'),
        'format': 'bestvideo[height=1080]+bestaudio/best[height=1080]',
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=True)
        title = info_dict.get('title', 'Unknown Title')
        description = info_dict.get('description', 'No Description')
        thumbnail_url = info_dict.get('thumbnail', '')

    thumbnail_path = None
    if thumbnail_url:
        response = requests.get(thumbnail_url)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            img = img.resize(thumbnail_size, Image.LANCZOS)
            thumbnail_path = os.path.join(thumbnail_output_dir, f"{serial}.jpg")
            img.save(thumbnail_path, "JPEG")

    return title, description, thumbnail_url, thumbnail_path
