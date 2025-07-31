from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status
from secrets import token_urlsafe

import logging
import json
import os

from functions.auth_functions import auth_check

from .models import MusicTempRecord, ArtistRecord, ArtistGenres, MusicAlbumRecord, MusicTrackRecord

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
            serial = None
            while serial is None:
                serial = token_urlsafe(16)
                if MusicTempRecord.objects.filter(serial=serial).exists():
                    serial = None
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
            logging.error(f"Error during video upload: {str(e)}")
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
            if not albums:
                return Response({'message': 'No music albums found'},
                                status=status.HTTP_404_NOT_FOUND)
            data = []
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
            return Response({"data":data, "message": "Music albums fetched successfully"},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during fetching music albums: {str(e)}")
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
            logging.error(f"Error during fetching music album data: {str(e)}")
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
            logging.error(f"Error during fetching music tracks: {str(e)}")
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
            return Response({"message": "Artist thumbnail fetched successfully"},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during fetching artist thumbnail: {str(e)}")
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
            logging.error(f"Error during fetching album thumbnail: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['GET'])
def get_track_data (request, serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            tracks = MusicTrackRecord.objects.filter(album_record=serial).all()
            if not tracks:
                return Response({'message': 'Track not found'},
                                status=status.HTTP_404_NOT_FOUND)
            data = []
            for track in tracks:
                data.append({
                    'track_serial': track.serial,
                    'track_number': track.track_number,
                    'track_name': track.track_name,
                    'track_duration': track.track_duration
                })
            return Response({"data": data, "message": "Track data fetched successfully"},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during fetching track data: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_track_preview(request, serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            track = MusicTrackRecord.objects.filter(serial=serial).first()
            if not track:
                return Response({'message': 'Track not found'},
                                status=status.HTTP_404_NOT_FOUND)
            file_path = track.track_location + track.serial + '.mp3'
            if not os.path.exists(file_path):
                return Response({'message': 'File not found'},
                                status=status.HTTP_404_NOT_FOUND)
            with open(file_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='audio/mpeg', status=status.HTTP_200_OK)
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                return response
            return Response({"message": "Track mp3 fetched successfully"},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during fetching track mp3: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            return Response({"message": "Artist data fetched successfully"},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during fetching artist data: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
