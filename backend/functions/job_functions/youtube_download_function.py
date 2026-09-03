import os
import requests
from io import BytesIO
from PIL import Image
import yt_dlp
import logging
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

def extract_clean_youtube_url(url):
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    video_id = qs.get("v", [""])[0]

    if not video_id:
        return url
    return f"https://www.youtube.com/watch?v={video_id}"

def process_youtube_video(
    video_url,
    video_output_dir=None,
    thumbnail_size=(320, 180),
    serial=None,
    thumbnail_output_dir=None
):
    clean_url = extract_clean_youtube_url(video_url)

    os.makedirs(video_output_dir, exist_ok=True)
    os.makedirs(thumbnail_output_dir, exist_ok=True)

    base_path = os.path.join(video_output_dir, serial)
    for ext in ["mp4", "mkv", "webm", "part", "ytdl"]:
        f = f"{base_path}.{ext}"
        if os.path.exists(f):
            try:
                os.remove(f)
                logger.info(f"Removed leftover file: {f}")
            except Exception as e:
                logger.warning(f"Unable to remove old file {f}: {e}")

    ydl_opts = {
        "outtmpl": os.path.join(video_output_dir, f"{serial}.%(ext)s"),
        "format": "bestvideo[height=1080]+bestaudio/best[height=1080]/best",
        "merge_output_format": "mp4",
        "continuedl": True,
        "overwrites": True,
        "quiet": True,
        "no_warnings": True,
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/115.0 Safari/537.36"
            ),
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(clean_url, download=True)
    except Exception as e:
        logger.error(f"yt-dlp failed: {clean_url} | Error: {e}")
        return None

    title = info_dict.get("title", "Unknown Title")
    description = info_dict.get("description", "No Description")
    thumbnail_url = info_dict.get("thumbnail", "")
    thumbnail_path = None
    
    video_id = info_dict.get("id", '')
    full_title = info_dict.get("fulltitle", '')
    alt_title = info_dict.get("alt_title", '')
    uploader = info_dict.get("uploader", '')
    uploader_id = info_dict.get("uploader_id", '')
    uploader_url = info_dict.get("uploader_url", '')
    video_license = info_dict.get("license", '')
    creators = info_dict.get("creator", [])
    upload_time = info_dict.get("timestamp", 0)
    upload_date = info_dict.get("upload_date", '')
    release_time = info_dict.get("release_timestamp", 0)
    release_date = info_dict.get("release_date", '')
    modified_timestamp = info_dict.get("modified_timestamp", 0)
    modified_date = info_dict.get("modified_date", '')
    channel = info_dict.get("channel", '')
    channel_id = info_dict.get("channel_id", '')
    channel_url = info_dict.get("channel_url", '')
    duration = info_dict.get("duration", 0)
    duration_formatted = info_dict.get("duration_string", '')
    age_limit = info_dict.get("age_limit", 0)
    media_type = info_dict.get("media_type", '')
    tags = info_dict.get("tags", [])
    categories = info_dict.get("categories", [])
    
    if thumbnail_url:
        try:
            resp = requests.get(thumbnail_url, timeout=10)
            resp.raise_for_status()
            img = Image.open(BytesIO(resp.content))
            img = img.resize(thumbnail_size, Image.LANCZOS)
            thumbnail_path = os.path.join(thumbnail_output_dir, f"{serial}.jpg")
            img.save(thumbnail_path, "JPEG")
        except Exception as e:
            logger.warning(f"Thumbnail failed for {video_url}: {e}")

    return {
        "title": title,
        "description": description,
        "thumbnail_url": thumbnail_url,
        "thumbnail_path": thumbnail_path,
        "video_id": video_id,
        "full_title": full_title,
        "alt_title": alt_title,
        "uploader": uploader,
        "uploader_id": uploader_id,
        "uploader_url": uploader_url,
        "video_license": video_license,
        "creators": creators,
        "upload_time": upload_time,
        "upload_date": upload_date,
        "release_time": release_time,
        "release_date": release_date,
        "modified_timestamp": modified_timestamp,
        "modified_date": modified_date,
        "channel": channel,
        "channel_id": channel_id,
        "channel_url": channel_url,
        "duration": duration,
        "duration_formatted": duration_formatted,
        "age_limit": age_limit,
        "media_type": media_type,
        "tags": tags,
        "categories": categories,
        "youtube_link": clean_url,
    }
