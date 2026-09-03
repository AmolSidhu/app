import requests
import os
import base64
import subprocess
from bs4 import BeautifulSoup as bs4
import re
import json
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()

def get_spotify_music_data(spotify_link):
    def convert_to_api_url(spotify_url):
        match = re.search(r'open\.spotify\.com/album/([a-zA-Z0-9]+)', spotify_url)
        if match:
            return f"https://api.spotify.com/v1/albums/{match.group(1)}"
        return spotify_url

    load_dotenv()
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

    if not client_id or not client_secret:
        return None

    auth_url = 'https://accounts.spotify.com/api/token'
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    response = requests.post(auth_url, headers=headers, data=data)

    if response.status_code != 200:
        return None

    access_token = response.json().get('access_token')
    if not access_token:
        return None

    headers = {"Authorization": f"Bearer {access_token}"}
    api_url = convert_to_api_url(spotify_link)
    album_response = requests.get(api_url, headers=headers)

    if album_response.status_code != 200:
        return None

    try:
        album_data = album_response.json()
    except json.JSONDecodeError:
        return None

    album_info = {
        "album_name": album_data.get('name', 'Unknown Album'),
        "release_date": album_data.get('release_date', 'Unknown Date'),
        "total_tracks": album_data.get('total_tracks', 0),
        "artists": [artist['name'] for artist in album_data.get('artists', [])],
        "artist_ids": [artist['id'] for artist in album_data.get('artists', [])],
        "popularity": album_data.get('popularity', 0),
        "album_id": album_data.get('id', 'Unknown ID'),
        "album_type": album_data.get('album_type', 'Unknown Type'),
        "album_spotify_url": album_data.get('external_urls', {}).get('spotify', 'No URL available'),
        "images": [image['url'] for image in album_data.get('images', [])],
        "tracks": []
    }

    for track in album_data.get('tracks', {}).get('items', []):
        album_info['tracks'].append({
            "track_name": track.get('name', 'Unknown Track'),
            "track_number": track.get('track_number', 0),
            "duration_ms": track.get('duration_ms', 0),
            "explicit": track.get('explicit', False),
            "preview_url": track.get('preview_url', 'No preview available'),
            "track_id": track.get('id', 'Unknown Track ID'),
        })

    artist_info_list = []
    for artist_id in album_info.get('artist_ids', []):
        artist_url = f"https://api.spotify.com/v1/artists/{artist_id}"
        artist_response = requests.get(artist_url, headers=headers)
        if artist_response.status_code != 200:
            continue

        try:
            artist_data = artist_response.json()
        except json.JSONDecodeError:
            continue

        artist_info = {
            "artist_name": artist_data.get('name', 'Unknown Artist'),
            "genres": artist_data.get('genres', []),
            "popularity": artist_data.get('popularity', 0),
            "followers": artist_data.get('followers', {}).get('total', 0),
            "spotify_url": artist_data.get('external_urls', {}).get('spotify', 'No URL available'),
            "images": [image['url'] for image in artist_data.get('images', [])],
            "artist_id": artist_id,
        }
        artist_info_list.append(artist_info)

    try:
        with open('json/directory.json', 'r') as f:
            directory = json.load(f)

        music_artist_thumbnail_dir = directory['music_artist_thumbnail_dir']
        music_album_thumbnail_dir = directory['music_album_thumbnail_dir']
        os.makedirs(music_artist_thumbnail_dir, exist_ok=True)
        os.makedirs(music_album_thumbnail_dir, exist_ok=True)

        if album_info['images']:
            album_thumb_url = album_info['images'][0]
            album_thumb_response = requests.get(album_thumb_url)
            if album_thumb_response.status_code == 200:
                album_filename = os.path.join(music_album_thumbnail_dir, f"{album_info['album_id']}.jpg")
                with open(album_filename, 'wb') as f:
                    f.write(album_thumb_response.content)
                album_info['album_image_location'] = music_album_thumbnail_dir

        for artist in artist_info_list:
            if artist['images']:
                artist_thumb_url = artist['images'][0]
                artist_thumb_response = requests.get(artist_thumb_url)
                if artist_thumb_response.status_code == 200:
                    artist_filename = os.path.join(music_artist_thumbnail_dir, f"{artist['artist_id']}.jpg")
                    with open(artist_filename, 'wb') as f:
                        f.write(artist_thumb_response.content)
                    artist['artist_image_location'] = music_artist_thumbnail_dir

    except Exception:
        pass

    return {
        "album_info": album_info,
        "artist_info": artist_info_list
    }

def get_apple_music_data(apple_link, tracks, apple_music_path):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(apple_link, headers=headers)
    if response.status_code != 200:
        return None

    soup = bs4(response.text, 'html.parser')
    script_tags = soup.find_all('script')

    json_data = None
    for script in script_tags:
        if 'AppleMusic' in script.text and 'albumName' in script.text:
            try:
                match = re.search(r'{"@context":.*}', script.text)
                if match:
                    json_data = json.loads(match.group())
                    break
            except json.JSONDecodeError:
                continue

    preview_urls = []
    for script in script_tags:
        if 'previewUrl' in script.text:
            preview_urls = re.findall(r'"previewUrl":"(https://audio-ssl.itunes.apple.com[^"]+)"', script.text)
            break

    if not preview_urls:
        return None

    if not os.path.exists(apple_music_path):
        os.makedirs(apple_music_path)

    for idx, url in enumerate(preview_urls):
        if idx >= len(tracks):
            break

        clean_url = url.replace('\\/', '/')
        filename_m4a = os.path.join(apple_music_path, f'temp_track_{idx+1}.m4a')
        filename_mp3 = os.path.join(apple_music_path, f"{tracks[idx]}.mp3")

        try:
            audio_response = requests.get(clean_url)
            with open(filename_m4a, 'wb') as f:
                f.write(audio_response.content)

            subprocess.run([
                'ffmpeg', '-y',
                '-i', filename_m4a,
                '-codec:a',
                'libmp3lame',
                '-qscale:a',
                '2',
                filename_mp3
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            os.remove(filename_m4a)
        except:
            continue

    if not json_data:
        return None

    album_data = {
        "album_name": json_data.get("name", ""),
        "album_image_location": json_data.get("image", {}).get("url", ""),
        "album_popularity": 0,
        "album_type": json_data.get("@type", "album"),
        "release_date": json_data.get("datePublished", ""),
        "total_tracks": len(tracks),
        "album_spotify_link": apple_link
    }

    return album_data