from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import FileResponse, HttpResponse
from django.utils import timezone
from rest_framework import status
from django.db import connection

import logging
import json
import os

from functions.auth_functions import auth_check
from functions.serial_default_generator import generate_serial_code
from functions.create_music_player_settings import create_default_music_player_settings
from functions.update_music_track_play_number import generate_music_track_play_number

from .queries import (get_custom_playlist_music_records_query, get_currently_playing_track_query,
                      get_listed_track_thumbnail_query, get_active_player_track_thumbnail_query)
from .models import (AddedFullTrackTemp, MusicTempRecord, ArtistRecord, ArtistGenres, MusicAlbumRecord,
                     MusicTrackRecord, MusicFullTrackRecord, CustomMusicPlaylist, CustomMusicPlaylistRecord,
                     CustomMusicPlayerSettings)

logger = logging.getLogger(__name__)

@api_view(['POST'])
def upload_music_links(request):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            serial = generate_serial_code(
                config_section='music',
                serial_key='temp_record_serial_code',
                model=MusicTempRecord,
                field_name='serial'
            )
            new_music_record = MusicTempRecord.objects.create(
                user=user,
                serial=serial,
                spotify_link=request.data.get('spotify_link', None),
                apple_link=request.data.get('apple_link', None),
                create_date=timezone.now()
            )
            new_music_record.save()
            return Response({"message": "Music links processed successfully"},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error during video upload: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_music_albums(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            albums = MusicAlbumRecord.objects.values(
                'serial', 'album_name', 'artist_record', 'album_popularity',
                'album_type', 'release_date', 'total_tracks', 'album_spotify_link',
                'artist_record'
            ).all()
            data = []
            if not albums:
                return Response({'message': 'No music albums found',
                                 'data': data},
                                status=status.HTTP_200_OK)
            for album in albums:
                data.append({
                    'serial': album['serial'],
                    'album_name': album['album_name'],
                    'artist_record': album['artist_record'],
                    'album_popularity': album['album_popularity'],
                    'album_type': album['album_type'],
                    'release_date': album['release_date'],
                    'total_tracks': album['total_tracks'],
                    'album_spotify_link': album['album_spotify_link'],
                    "artist_record": album['artist_record']
                })
                if not data:
                    return Response({'message': 'No music albums have been added yet',
                                     'data': []},
                                    status=status.HTTP_200_OK)
            return Response({"data":data, "message": "Music albums fetched successfully"},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error during fetching music albums: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['GET'])
def get_music_album_data(request, serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            return Response({"message": "Music album data fetched successfully"},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error during fetching music album data: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_music_tracks(request, serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            return Response({"message": "Music tracks fetched successfully"},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error during fetching music tracks: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_artist_thumbnail(request, serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            artist_record = ArtistRecord.objects.filter(serial=serial).first()
            if not artist_record:
                return Response({'message': 'Artist not found'},
                                status=status.HTTP_404_NOT_FOUND)
            file_path = artist_record.artist_image_location + artist_record.serial + '.jpg'
            if not os.path.exists(file_path):
                return Response({'message': 'File not found'},
                                status=status.HTTP_404_NOT_FOUND)
            with open(file_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='image/jpeg', status=status.HTTP_200_OK)
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                return response
        except Exception as e:
            logger.error(f"Error during fetching artist thumbnail: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_album_thumbnail(request, serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            album_record = MusicAlbumRecord.objects.filter(serial=serial).first()
            if not album_record:
                return Response({'message': 'Artist not found'},
                                status=status.HTTP_404_NOT_FOUND)
            file_path = album_record.album_image_location + album_record.serial + '.jpg'
            if not os.path.exists(file_path):
                return Response({'message': 'File not found'},
                                status=status.HTTP_404_NOT_FOUND)
            with open(file_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='image/jpeg', status=status.HTTP_200_OK)
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                return response
            return Response({"message": "Album thumbnail fetched successfully"},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error during fetching album thumbnail: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['GET'])
def get_track_data(request, serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            tracks = MusicTrackRecord.objects.filter(album_record=serial).all().order_by('track_number')
            if not tracks:
                return Response({'message': 'Track not found'},
                                status=status.HTTP_404_NOT_FOUND)
            data = []
            for track in tracks:
                data.append({
                    'track_serial': track.serial,
                    'track_number': track.track_number,
                    'track_name': track.track_name,
                    'track_duration': track.track_duration,
                    'full_track_added': track.full_track_added
                })
            return Response({"data": data, "message": "Track data fetched successfully"},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error during fetching track data: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_track_preview(request, serial):
    if request.method == 'GET':
        try:
            token = (
                request.headers.get('Authorization')
                or request.GET.get('token')
            )
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': auth_response['error']},
                                status=status.HTTP_401_UNAUTHORIZED)
            track = MusicTrackRecord.objects.filter(
                serial=serial).first()
            if not track:
                return Response(
                    {'message': 'Track not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            file_path = os.path.join(
                track.track_location,
                f'{track.serial}.mp3'
            )
            if track.full_track_added:
                file_path = os.path.join(track.full_track_location,
                                         f'{track.full_track_serial.serial}.mp3')
            if not os.path.exists(file_path):
                return Response({'message': 'File not found'},
                                status=status.HTTP_404_NOT_FOUND)
            response = FileResponse(
                open(file_path, 'rb'),
                content_type='audio/mpeg'
            )
            response['Accept-Ranges'] = 'bytes'
            response['Access-Control-Allow-Origin'] = '*'
            return response
        except Exception as e:
            logger.error(f'Error during fetching track mp3: {e}')
            return Response(
                {'message': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['GET'])
def get_artist_data(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            artist_records = ArtistRecord.objects.all()
            if not artist_records:
                return Response({'message': 'No artist records found'},
                                status=status.HTTP_200_OK)
            return Response({"message": "Artist data fetched successfully"},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error during fetching artist data: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def add_full_track(request, track_serial):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response(
                    {'message': auth_response["error"]},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            user = auth_response['user']
            track = MusicTrackRecord.objects.filter(
                serial=track_serial
            ).first()
            if not track:
                return Response(
                    {'message': 'Track not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            with open('json/directory.json', 'r') as f:
                directory = json.load(f)
            mp3_directory = directory['music_upload_track_match_dir']
            os.makedirs(mp3_directory, exist_ok=True)
            track_record = MusicTrackRecord.objects.filter(
                serial=track_serial
            ).first()
            if not track_record:
                return Response(
                    {'message': 'Track record not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            full_track_exists = AddedFullTrackTemp.objects.filter(
                track=track_record
            ).exists()
            if full_track_exists:
                return Response(
                    {'message': 'Full track already exists for this track'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serial = generate_serial_code(
                config_section='music',
                serial_key='full_uploaded_track_serial_code',
                model=AddedFullTrackTemp,
                field_name='serial'
            )
            uploaded_file = request.FILES.get('track_file')
            youtube_link = request.data.get('youtube_link')
            if not uploaded_file and not youtube_link:
                return Response(
                    {'message': 'Either track file or youtube link must be provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            file_record = False
            link_record = False
            mp3_file_added = False
            file_path = None
            if uploaded_file:
                file_extension = os.path.splitext(uploaded_file.name)[1]
                file_path = os.path.normpath(
                    os.path.join(mp3_directory, serial + file_extension)
                )
                with open(file_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
                file_record = True
                mp3_file_added = True
            if youtube_link:
                link_record = True
            new_full_track = AddedFullTrackTemp.objects.create(
                serial=serial,
                track=track_record,
                user=user,
                file_record=file_record,
                link_record=link_record,
                mp3_file_added=mp3_file_added,
                file_path=mp3_directory,
                youtube_link=youtube_link,
                record_status='pending'
            )
            new_full_track.save()
            return Response(
                {"message": "Full song added successfully"},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Error during adding full song: {str(e)}")
            return Response(
                {'message': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['POST'])
def create_custom_music_playlist(request):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            serial = generate_serial_code(
                config_section='music',
                serial_key='custom_music_playlist_serial_code',
                model=CustomMusicPlaylist,
                field_name='serial'
            )
            new_music_playlist = CustomMusicPlaylist.objects.create(
                serial=serial,
                user=user,
                playlist_name=request.data.get('playlist_name', ''),
                playlist_description=request.data.get('playlist_description', ''),
                create_date=timezone.now()
            )
            new_music_playlist.save()
            return Response({"message": "Custom music playlist created successfully"},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error during creating custom music playlist: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['POST'])
def add_track_to_custom_music_playlist(request, playlist_serial, track_serial):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            existing_playlist = CustomMusicPlaylist.objects.filter(
                serial=playlist_serial, user=user).first()
            if not existing_playlist:
                return Response({'message': 'Custom music playlist not found'},
                                status=status.HTTP_404_NOT_FOUND)
            existing_track = MusicTrackRecord.objects.filter(
                serial=track_serial).first()
            if not existing_track:
                return Response({'message': 'Music track not found'},
                                status=status.HTTP_404_NOT_FOUND)
            serial = generate_serial_code(
                config_section='music',
                serial_key='custom_music_playlist_record_serial_code',
                model=CustomMusicPlaylistRecord,
                field_name='serial'
            )
            new_playlist_record = CustomMusicPlaylistRecord.objects.create(
                serial=serial,
                playlist=existing_playlist,
                track=existing_track,
                added_date=timezone.now()
            )
            new_playlist_record.save()
            return Response({"message": "Track added to custom playlist successfully"},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error during adding track to custom playlist: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def delete_track_from_custom_playlist(request, playlist_serial, track_serial):
    if request.method == 'DELETE':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            existing_playlist = CustomMusicPlaylist.objects.filter(
                serial=playlist_serial, user=user).first()
            if not existing_playlist:
                return Response({'message': 'Custom music playlist not found'},
                                status=status.HTTP_400_BAD_REQUEST)
            existing_track = CustomMusicPlaylistRecord.objects.filter(
                track=track_serial).first()
            if not existing_track:
                return Response({'message': 'Music track not found'},
                                status=status.HTTP_400_BAD_REQUEST)
            existing_track.delete()
            return Response({"message": "Track removed from custom playlist successfully"},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error during removing track from custom playlist: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_custom_music_playlists(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            playlists = CustomMusicPlaylist.objects.filter(user=user).all()
            if not playlists:
                return Response({'message': 'No custom music playlists found'},
                                status=status.HTTP_200_OK)
            data = []
            for playlist in playlists:
                data.append({
                    'serial': playlist.serial,
                    'playlist_name': playlist.playlist_name,
                    'playlist_description': playlist.playlist_description,
                    'create_date': playlist.create_date
                })
            return Response({"message": "Custom music playlists fetched successfully",
                             "data": data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error during fetching custom music playlists: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['GET'])
def get_not_added_to_custom_music_playlists(request, track_serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            track_record = MusicTrackRecord.objects.filter(serial=track_serial).first()
            if not track_record:
                return Response({'message': 'Track record not found'},
                                status=status.HTTP_404_NOT_FOUND)
            not_added_playlists = CustomMusicPlaylist.objects.filter(
                user=user
            ).exclude(
                custommusicplaylistrecord__track_id=track_record
            ).all()
            if not not_added_playlists:
                return Response({'message': 'All playlists already contain this track'},
                                status=status.HTTP_200_OK)
            data = []
            for playlist in not_added_playlists:
                data.append({
                    'serial': playlist.serial,
                    'playlist_name': playlist.playlist_name,
                })
            return Response({"message": "Custom music playlist tracks fetched successfully",
                             "data": data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error during fetching custom music playlist tracks: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['GET'])
def get_added_to_custom_music_playlists(request, track_serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            track_record = MusicTrackRecord.objects.filter(serial=track_serial).first()
            if not track_record:
                return Response({'message': 'Track record not found'},
                                status=status.HTTP_404_NOT_FOUND)
            added_playlists = CustomMusicPlaylist.objects.filter(
                user=user,
                custommusicplaylistrecord__track_id=track_record
            ).all()
            if not added_playlists:
                return Response({'message': 'No playlists contain this track'},
                                status=status.HTTP_200_OK)
            data = []
            for playlist in added_playlists:
                data.append({
                    'serial': playlist.serial,
                    'playlist_name': playlist.playlist_name,
                })
            return Response({"message": "Custom music playlist tracks fetched successfully",
                             "data": data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error during fetching custom music playlist tracks: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_custom_music_playlist_tracks(request, playlist_serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            username = user.username
            playlist_record = CustomMusicPlaylist.objects.filter(
                serial=playlist_serial, user=user).first()
            if not playlist_record:
                return Response({'message': 'Custom music playlist not found'},
                                status=status.HTTP_400_BAD_REQUEST)
            query = get_custom_playlist_music_records_query()
            with connection.cursor() as cursor:
                cursor.execute(query, [playlist_serial, username])
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                data = [dict(zip(columns, row)) for row in rows]
            return Response({"message": "Custom music playlist tracks fetched successfully",
                             "data": data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error during fetching custom music playlist tracks: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_custom_music_player_settings(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            settings_record = CustomMusicPlayerSettings.objects.filter(user=user).first()
            if not settings_record:
                created = create_default_music_player_settings(user)
                if not created:
                    return Response({'message': 'Failed to create default music player settings'},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                settings_record = CustomMusicPlayerSettings.objects.filter(user=user).first()
            data = {
                'serial': settings_record.serial,
                'oder_playback': settings_record.order_playback,
                'shuffle_playback': settings_record.shuffle_playback,
            }
            return Response({"message": "Custom music player settings fetched successfully",
                             "data": data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error during fetching custom music player settings: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_currently_playing_track_data(request, playlist_serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            current_track = CustomMusicPlaylistRecord.objects.filter(
                playlist=playlist_serial,
                current_track=True).first()
            data = {}
            query = get_currently_playing_track_query()
            with connection.cursor() as cursor:
                cursor.execute(query, [playlist_serial])
                columns = [col[0] for col in cursor.description]
                row = cursor.fetchone()
                if row:
                    data = dict(zip(columns, row))
                return Response({"data": data,
                                    "message": "Currently playing track data fetched successfully"},
                                status=status.HTTP_200_OK)
            if not current_track:
                return Response({'message': 'No currently playing track found',
                                 'data': data},
                                status=status.HTTP_200_OK)
            return Response({"message": "Currently playing track data fetched successfully"},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error during fetching currently playing track data: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_listed_track_thumbnails(request, playlist_serial, track_serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': auth_response['error']},
                                status=status.HTTP_401_UNAUTHORIZED)
            query = get_listed_track_thumbnail_query()
            with connection.cursor() as cursor:
                cursor.execute(query, [playlist_serial, track_serial])
                row = cursor.fetchone()
            if not row:
                return Response({'message': 'Custom music playlist track not found'},
                                status=status.HTTP_404_NOT_FOUND)
            album_serial, thumbnail_location = row
            file_path = os.path.join(thumbnail_location,f"{album_serial}.jpg")
            if not os.path.exists(file_path):
                return Response({'message': 'File not found'},
                                status=status.HTTP_404_NOT_FOUND)
            return FileResponse(open(file_path, 'rb'),
                                content_type='image/jpeg',
                                status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error during fetching listed track thumbnails: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_currently_streaming_track_thumbnail(request, playlist_serial, track_serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            query = get_active_player_track_thumbnail_query()
            with connection.cursor() as cursor:
                cursor.execute(query, [playlist_serial, track_serial])
                row = cursor.fetchone()
            if not row:
                return Response({'message': 'Custom music playlist track not found'},
                                status=status.HTTP_404_NOT_FOUND)
            album_serial, thumbnail_location = row
            file_path = os.path.join(thumbnail_location,f"{album_serial}.jpg")
            if not os.path.exists(file_path):
                return Response({'message': 'File not found'},
                                status=status.HTTP_404_NOT_FOUND)
            return FileResponse(open(file_path, 'rb'),
                                content_type='image/jpeg',
                                status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error during fetching currently playing track thumbnail: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_currently_streaming_track(request, track_serial):
    if request.method == 'GET':
        try:
            track_record = ''
        except Exception as e:
            logger.error(f"Error during fetching currently streaming track: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_next_track_in_custom_playlist(request, playlist_serial, current_track_serial, current_track_number):
    if request.method == 'GET':
        try:
            pass
        except Exception as e:
            logger.error(f"Error during fetching next track in custom playlist: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['GET'])
def get_previous_track_in_custom_playlist(request, playlist_serial, current_track_serial, current_track_number):
    if request.method == 'GET':
        try:
            pass
        except Exception as e:
            logger.error(f"Error during fetching previous track in custom playlist: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def update_custom_music_player_settings(request):
    if request.method == 'PATCH':
        try:
            pass
        except Exception as e:
            logger.error(f"Error during updating custom music player settings: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def update_played_tracks(request, playlist_serial, track_serial):
    if request.method == 'PATCH':
        try:
            pass
        except Exception as e:
            logger.error(f"Error during updating played song: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def save_currently_streaming_track(request, playlist_serial, track_serial):
    if request.method == 'PATCH':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
        except Exception as e:
            logger.error(f"Error during saving currently streaming track: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)