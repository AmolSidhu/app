from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import status
from secrets import token_urlsafe

import logging
import json
import os

from functions.auth_functions import auth_check

from .models import YoutubeTempRecord, YoutubeVideoRecord, YoutubeLists, YoutubeListRecord

logger = logging.getLogger(__name__)

@api_view(['POST'])
def upload_youtube_video(request):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response(auth_response['error'])
            user = auth_response['user']
            serial = None
            while serial is None:
                serial = token_urlsafe(16)
                if YoutubeTempRecord.objects.filter(serial=serial).exists():
                    serial = None
                if YoutubeVideoRecord.objects.filter(serial=serial).exists():
                    serial = None
            with open('directory.json', 'r') as f:
                directory = json.load(f)
            video_dir = directory['youtube_video_dir']
            thumbnail_dir = directory['youtube_thumbnail_dir']
            if not os.path.exists(video_dir):
                os.makedirs(video_dir)
            if not os.path.exists(thumbnail_dir):
                os.makedirs(thumbnail_dir)
            temp_record = YoutubeTempRecord.objects.create(
                serial=serial,
                user=user,
                youtube_video_location=video_dir,
                youtube_link=request.data.get('youtube_link'),
                youtube_thumbnail_location=thumbnail_dir,
                add_to_playlists =request.data.get('add_to_playlists'),
            )
            temp_record.save()
            return Response({'message': 'Youtube video upload started successfully.'},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f'Error in create_youtube_playlist: {e}')
            return Response({'message': 'An error occurred while creating the YouTube playlist.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def create_youtube_playlist(request):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response(auth_response['error'])
            user = auth_response['user']
            serial = None
            while serial is None:
                serial = token_urlsafe(16)
                if YoutubeLists.objects.filter(serial=serial).exists():
                    serial = None
            playlist_record = YoutubeLists.objects.create(
                serial=serial,
                user=user,
                name=request.data.get('title'),
                description=request.data.get('description'),
            )
            playlist_record.save()
            return Response({'message': 'Playlist created successfully.'},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f'Error in upload_video: {e}')
            return Response({'message': 'An error occurred while creating the YouTube playlist.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def add_video_to_youtube_playlist(request, video_serial, playlist_serial):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response(auth_response['error'],
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            youtube_video_record = YoutubeVideoRecord.objects.filter(serial=video_serial).first()
            if not youtube_video_record:
                return Response({'message': 'Video not found.'},
                                status=status.HTTP_404_NOT_FOUND)
            youtube_playlist_record = YoutubeLists.objects.filter(serial=playlist_serial).first()
            if not youtube_playlist_record:
                return Response({'message': 'Playlist not found.'},
                                status=status.HTTP_404_NOT_FOUND)
            serial = None
            while serial is None:
                serial = token_urlsafe(16)
                if YoutubeListRecord.objects.filter(serial=serial).exists():
                    serial = None
            new_playlist_record = YoutubeListRecord.objects.create(
                serial=serial,
                youtube_list=youtube_playlist_record,
                youtube_video=youtube_video_record
            )
            new_playlist_record.save()
            return Response({'message': 'Video added to playlist successfully.'},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f'Error in add_video_to_playlist: {e}')
            return Response({'message': 'An error occurred while adding the video to the YouTube playlist.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_youtube_playlists(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response(auth_response['error'],
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            youtube_playlists = YoutubeLists.objects.filter(user=user).values(
                'serial', 'name', 'description')
            data = []
            for playlist in youtube_playlists:
                playlist_record = {
                    'serial': playlist['serial'],
                    'name': playlist['name'],
                    'description': playlist['description']
                }
                data.append(playlist_record)
            return Response({'message': 'Youtube playlists fetched successfully.',
                            'data': data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error in get_youtube_playlists: {e}')
            return Response({'message': 'An error occurred while fetching the YouTube playlists.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_playlist_videos(request, playlist_serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response(auth_response['error'],
                                status=status.HTTP_401_UNAUTHORIZED)
            youtube_playlist = YoutubeLists.objects.filter(
                serial=playlist_serial).first()
            if not youtube_playlist:
                return Response({'message': 'Playlist not found.'},
                                status=status.HTTP_404_NOT_FOUND)
            offset = int(request.query_params.get('offset', 0))
            limit = int(request.query_params.get('limit', 5))
            youtube_videos_qs = YoutubeListRecord.objects.filter(
                youtube_list=youtube_playlist
            ).values(
                'youtube_video__serial',
                'youtube_video__title',
                'youtube_video__description',
                'youtube_video__thumbnail_path',
                'youtube_video__video_path'
            )
            total_count = youtube_videos_qs.count()
            youtube_videos = youtube_videos_qs[offset:offset+limit]
            data = [{
                'serial': v['youtube_video__serial'],
                'title': v['youtube_video__title'],
                'description': v['youtube_video__description'],
                'thumbnail_location': v['youtube_video__thumbnail_path'],
                'video_location': v['youtube_video__video_path']
            } for v in youtube_videos]
            return Response({
                'message': 'Videos fetched successfully.',
                'data': data,
                'total': total_count
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error in get_playlist_videos: {e}')
            return Response({'message': 'Internal server error.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_youtube_thumbnail(request, serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response(auth_response['error'],
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            youtube_video = YoutubeVideoRecord.objects.filter(serial=serial).first()
            if not youtube_video:
                return Response({'message': 'Video not found.'},
                                status=status.HTTP_404_NOT_FOUND)
            thumbnail_location = youtube_video.thumbnail_path + youtube_video.serial + '.jpg'
            if not os.path.exists(thumbnail_location):
                return Response({'message': 'Thumbnail not found.'},
                                status=status.HTTP_404_NOT_FOUND)
            with open(thumbnail_location, 'rb') as f:
                return HttpResponse(f.read(), content_type='image/jpeg')
        except Exception as e:
            logger.error(f'Error in get_youtube_thumbnail: {e}')
            return Response({'message': 'An error occurred while fetching the YouTube thumbnail.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def watch_youtube_video(request, serial, token):
    if request.method == 'PATCH':
        try:
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response(auth_response['error'])
            user = auth_response['user']
        except Exception as e:
            logger.error(f'Error in watch_youtube_video: {e}')
            return Response({'message': 'An error occurred while updating the YouTube video.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def update_youtube_playback_time(request, serial):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response(auth_response['error'],
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            youtube_video = YoutubeVideoRecord.objects.filter(serial=serial).first()
            if not youtube_video:
                return Response({'message': 'Video not found.'},
                                status=status.HTTP_404_NOT_FOUND)
            youtube_video.video_stop_time = request.data.get('currentTime')
            youtube_video.save()
            return Response({'message': 'Youtube video playback time updated successfully.'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error in update_youtube_playback_time: {e}')
            return Response({'message': 'An error occurred while updating the YouTube video playback time.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def delete_youtube_video_from_playlist(request, video_serial, playlist_serial):
    if request.method == 'DELETE':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response(auth_response['error'],
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            youtube_video = YoutubeVideoRecord.objects.filter(serial=video_serial).first()
            if not youtube_video:
                return Response({'message': 'Video not found.'},
                                status=status.HTTP_404_NOT_FOUND)
            youtube_playlist = YoutubeLists.objects.filter(serial=playlist_serial).first()
            if not youtube_playlist:
                return Response({'message': 'Playlist not found.'},
                                status=status.HTTP_404_NOT_FOUND)
            youtube_list_record = YoutubeListRecord.objects.filter(
                youtube_video=youtube_video,
                youtube_list=youtube_playlist
            ).first()
            if not youtube_list_record:
                return Response({'message': 'Video not found in the playlist.'},
                                status=status.HTTP_404_NOT_FOUND)
            youtube_list_record.delete()
            return Response({'message': 'Video removed from playlist successfully.'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error in remove_video_from_playlist: {e}')
            return Response({'message': 'An error occurred while removing the video from the YouTube playlist.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
