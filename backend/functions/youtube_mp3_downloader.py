import os
import yt_dlp

def youtube_mp3_downloader(url=None, output_folder=None, serial=None):
    os.makedirs(output_folder, exist_ok=True)

    setup_options = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(output_folder, serial + ".mp3"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": False,
        "noplaylist": True,
    }

    youtube_download = yt_dlp.YoutubeDL(setup_options)
    youtube_download.download([url])
