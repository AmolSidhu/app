from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.http import StreamingHttpResponse
from django.http import JsonResponse
from wsgiref.util import FileWrapper
from io import BytesIO
import logging
import os
import mimetypes
import re

from functions.auth_functions import auth_check
from videos.models import VideoRecord, VideoHistory

logger = logging.getLogger(__name__)

@api_view(['GET'])
def get_video_stream(request, serial, permission):
    if request.method == 'GET':
        try:
            token = permission
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            video = VideoRecord.objects.filter(video_serial=serial).first()
            if not video:
                return JsonResponse({'message': 'Video not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            video_path = os.path.join(video.video_location, f'{video.video_serial}.mp4')
            if not os.path.exists(video_path):
                return JsonResponse({'message': 'Video file not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            resume = request.GET.get('resume', 'false').lower() == 'true'
            resume_time = 0
            if resume:
                video_history = VideoHistory.objects.filter(user=user, serial=video).first()
                if video_history:
                    resume_time = video_history.video_stop_time
            size = os.path.getsize(video_path)
            content_type, _ = mimetypes.guess_type(video_path)
            range_header = request.META.get('HTTP_RANGE', '').strip()
            range_match = re.match(r'bytes=(\d+)-(\d+)?', range_header)
            if range_match:
                first_byte, last_byte = range_match.groups()
                first_byte = int(first_byte) if first_byte else 0
                last_byte = int(last_byte) if last_byte else size - 1
                last_byte = min(last_byte, size - 1)
                length = last_byte - first_byte + 1
                with open(video_path, 'rb') as f:
                    f.seek(first_byte)
                    data = f.read(last_byte - first_byte + 1)
                response = StreamingHttpResponse(FileWrapper(BytesIO(data)),
                                                    status=status.HTTP_206_PARTIAL_CONTENT,
                                                    content_type=content_type)
                response['Content-Length'] = str(length)
                response['Content-Range'] = f'bytes {first_byte}-{last_byte}/{size}'
            else:
                response = StreamingHttpResponse(FileWrapper(open(video_path, 'rb')),
                                                    content_type=content_type)
                response['Content-Length'] = str(size)
            response['Accept-Ranges'] = 'bytes'
            response['Resume-Time'] = str(resume_time)
            return response
        except Exception as e:
            logging.error(f"Error during video streaming: {str(e)}")
            return JsonResponse({'message': 'Internal server error'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_video_history(request, serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            video = VideoRecord.objects.filter(video_serial=serial).first()
            if not video:
                return JsonResponse({'message': 'Video not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            instance=video.video_instance
            video_history = VideoHistory.objects.filter(user=user,
                                                        serial=serial,
                                                        video_serial_id=instance).first()
            if not video_history:
                return JsonResponse({'video_stop_time': 0},
                                    status=status.HTTP_200_OK)
            return JsonResponse({'video_stop_time': video_history.video_stop_time},
                                status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error fetching video history: {str(e)}")
            return JsonResponse({'message': 'Internal server error'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def update_playback_time(request, serial):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            video_stop_time = request.data.get('currentTime')
            video = VideoRecord.objects.filter(video_serial=serial).first()
            if not video:
                return JsonResponse({'message': 'Video not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            history = VideoHistory.objects.filter(user=user,
                                                    serial=serial).first()
            if not history:
                history = VideoHistory.objects.create(user=user,
                                                        master_record=video.master_record,
                                                        video_stop_time=video_stop_time,
                                                        serial=video
                                                        )
            else:
                history.video_stop_time = video_stop_time
                history.save()
            return JsonResponse({'message': 'Playback time updated'},
                                status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during video upload: {str(e)}")
            return JsonResponse({'message': 'Internal server error'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
