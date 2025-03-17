from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

import logging

from functions.auth_functions import auth_check

logger = logging.getLogger(__name__)

@api_view(['POST'])
def create_youtube_playlist(request):
    try:
        token = request.headers.get('Authorization')
        auth_response = auth_check(token)
        if 'error' in auth_response:
            return Response(auth_response['error'])
        user = auth_response['user']
    except Exception as e:
        logger.error(f'Error in create_youtube_playlist: {e}')
        return Response({'message': 'An error occurred while creating the YouTube playlist.'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def upload_video(request):
    try:
        token = request.headers.get('Authorization')
        auth_response = auth_check(token)
        if 'error' in auth_response:
            return Response(auth_response['error'])
        user = auth_response['user']
    except Exception as e:
        logger.error(f'Error in upload_video: {e}')
        return Response({'message': 'An error occurred while uploading the video.'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def add_video_to_playlist(request, serial):
    try:
        token = request.headers.get('Authorization')
        auth_response = auth_check(token)
        if 'error' in auth_response:
            return Response(auth_response['error'], status=status.HTTP_401_UNAUTHORIZED)
        user = auth_response['user']
    except Exception as e:
        logger.error(f'Error in add_video_to_playlist: {e}')
        return Response({'message': 'An error occurred while adding the video to the YouTube playlist.'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_youtube_playlists(request):
    try:
        token = request.headers.get('Authorization')
        auth_response = auth_check(token)
        if 'error' in auth_response:
            return Response(auth_response['error'], status=status.HTTP_401_UNAUTHORIZED)
        user = auth_response['user']
    except Exception as e:
        logger.error(f'Error in get_youtube_playlists: {e}')
        return Response({'message': 'An error occurred while fetching the YouTube playlists.'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_playlist_videos(request, playlist_serial):
    try:
        token = request.headers.get('Authorization')
        auth_response = auth_check(token)
        if 'error' in auth_response:
            return Response(auth_response['error'], status=status.HTTP_401_UNAUTHORIZED)
        user = auth_response['user']
    except Exception as e:
        logger.error(f'Error in get_playlist_videos: {e}')
        return Response({'message': 'An error occurred while fetching the videos in the YouTube playlist.'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def watch_youtube_video(request, video_serial, token):
    try:
        auth_response = auth_check(token)
        if 'error' in auth_response:
            return Response(auth_response['error'])
        user = auth_response['user']
    except Exception as e:
        logger.error(f'Error in watch_youtube_video: {e}')
        return Response({'message': 'An error occurred while updating the YouTube video.'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)