from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from datetime import datetime
from secrets import token_hex

import hashlib
import logging
import json

from functions.auth_functions import auth_check
from functions.auth_functions import token_generator
from videos.models import Video, VideoRecord
from user.models import Credentials

logger = logging.getLogger(__name__)

@api_view(['POST'])
def import_identifier_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            data = data['data']
            with open('directory.json', 'r') as f:
                directory = json.load(f)                
            temp_file = token_hex(8)
            with open(f'{directory["temp_json_dir"]}/{temp_file}.json', 'w') as f:
                json.dump(data, f)
            return Response({'success': 'Data imported'},
                                status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(e)
            return Response({'error': 'An error occurred'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def update_episode_record(request, season, episode):
    if request.method == 'PATCH':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            master_serial = request.data['master_serial']
            video_record = Video.objects.filter(serial=master_serial).first()
            if not video_record or video_record.uploaded_by_id != user.id:
                return Response({'message': 'Video not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            video_serial = request.data['episode_serial']
            episode_record = VideoRecord.objects.filter(batch_instance=video_record.id,
                                                        episode=episode,
                                                        season=season,
                                                        video_serial=video_serial).first()
            if not episode_record:
                return Response({'message': 'Episode not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            data = request.data
            episode_record.episode = data['new_episode']
            episode_record.season = data['new_season']
            episode_record.save()
            video_record.update_series = False
            video_record.save()
            return Response({'message': 'Episode record updated successfully'},
                                status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during video upload: {str(e)}")
            return Response({'message': 'Internal server error'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['DELETE'])
def delete_video_record(request, serial):
    if request.method == 'DELETE':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            video_record = Video.objects.filter(serial=serial).first()  
            if not video_record or video_record.uploaded_by_id != user.id:
                return Response({'message': 'Video not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            video_record.current_status = 'Deleted'
            video_record.save()
            return Response({'message': 'Video deleted'},
                                status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during video upload: {str(e)}")
            return Response({'message': 'Internal server error'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def delete_episode_record(request, serial, season, episode):
    if request.method == 'DELETE':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            video_serial = request.data['episode_serial']
            video_record = Video.objects.filter(serial=serial).first()
            if not video_record or video_record.uploaded_by_id != user.id:
                return Response({'message': 'Video not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            episode_record = VideoRecord.objects.filter(batch_instance=video_record.id,
                                                        episode=episode,
                                                        season=season,
                                                        video_serial=video_serial).first()
            if not episode_record:
                return Response({'message': 'Episode not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            episode_record.current_status = 'Deleted'
            video_record.update_series = False
            video_record.save()
            return Response({'message': 'Episode deleted'},
                                status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during episode deletion: {str(e)}")
            return Response({'message': 'Internal server error'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def delete_season_records(request, serial):
    if request.method == 'DELETE':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            master_id = request.data['master_id']
            season = request.data['season']
            video_record = Video.objects.filter(id=master_id,
                                                serial=serial).first()
            if not video_record or video_record.uploaded_by != user.username:
                return Response({'message': 'Video not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            season_records = VideoRecord.objects.filter(batch_instance=master_id,
                                                       season=season).all()
            if not season_records:
                return Response({'message': 'Season not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            for season_record in season_records:
                season_record.current_status = 'Deleted'
                season_record.save()
            return Response({'message': 'Season deleted'},
                                status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during season deletion: {str(e)}")
            return Response({'message': 'Internal server error'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def change_email(request):
    if request.method == 'PATCH':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            data = request.data
            new_email = data['new_email']
            valid_email = Credentials.objects.filter(email=new_email).first()
            if valid_email:
                return Response({'message': 'Email already in use',},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                user.email = new_email
                user.save()
                token = token_generator(user.username, user.email)
            return Response({'message': 'Email changed successfully',
                                 'token': token},
                                status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during email change: {str(e)}")
            return Response({'message': 'Internal server error'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['PATCH'])
def change_username(request):
    if request.method == 'PATCH':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            data = request.data
            new_username = data['new_username']
            valid_username = Credentials.objects.filter(username=new_username).first()
            if valid_username:
                return Response({'message': 'Username already in use'},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                user.username = new_username
                user.save()
                token = token_generator(user.username, user.email)
            return Response({'message': 'Username changed successfully',
                                'token': token},
                                status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during video upload: {str(e)}")
            return Response({'message': 'Internal server error'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def delete_account(request):
    if request.method == 'PATCH':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            if hashlib.sha256(request.data['password'].encode()).hexdigest() != user.password:
                return Response({'message': 'Incorrect password'},
                                    status=status.HTTP_400_BAD_REQUEST)
            if request.data['confirmation'] != 'DELETE':
                return Response({'message': 'Confirmation does not match'},
                                    status=status.HTTP_400_BAD_REQUEST)
            user.user_status = 'D'
            user.user_status_updated_date = datetime.now()
            return Response({'message': 'Account marked for deletion'},
                                status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during account deletion: {str(e)}")
            return Response({'message': 'Internal server error'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_video_list(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            user_id = user.username
            videos = Video.objects.filter(uploaded_by=user_id).all()
            video_list = []
            for video in videos:
                video_list.append({'serial': video.serial,
                                    'title': video.title,
                                    'description': video.description,
                                    'uploaded_by': video.uploaded_by,
                                    'uploaded_date': video.uploaded_date,
                                    'status': video.status})
            return Response({'videos': video_list},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during video list retrieval: {str(e)}")
            return Response({'message': 'Internal server error'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def update_video_record(request, serial):
    if request.method == 'PATCH':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            video = Video.objects.filter(serial=serial).first()
            if not video or video.uploaded_by != user.username:
                return Response({'message': 'Video not found'},
                                status=status.HTTP_404_NOT_FOUND)
            data = request.data
            video.title = data['title']
            video.description = data['description']
            video.save()
            return Response({'message': 'Video record updated successfully'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during video update: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_full_video_record(request, serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            video = Video.objects.filter(serial=serial).first()
            if not video or video.uploaded_by != user.username:
                return Response({'message': 'Video not found'},
                                status=status.HTTP_404_NOT_FOUND)
            video_record = VideoRecord.objects.filter(batch_instance=video.id).all()
            video_data = []
            for record in video_record:
                video_data.append({'episode': record.episode,
                                    'season': record.season,
                                    'video_serial': record.video_serial,
                                    'status': record.current_status})
            return Response({'video_data': video_data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during video data request: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_episode_records(request, serial, season):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            video = Video.objects.filter(serial=serial).first()
            if not video or video.uploaded_by != user.username:
                return Response({'message': 'Video not found'},
                                status=status.HTTP_404_NOT_FOUND)
            video_record = VideoRecord.objects.filter(master_record=serial,
                                                    season=season).all()
            video_data = []
            for record in video_record:
                video_data.append({'episode': record.episode,
                                    'season': record.season,
                                    'video_serial': record.video_serial,
                                    'status': record.current_status})
            return Response({'video_data': video_data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during episode data request: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def update_episode_record(request, serial, season, episode):
    if request.method == 'PATCH':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            video = Video.objects.filter(serial=serial).first()
            if not video or video.uploaded_by != user.username:
                return Response({'message': 'Video not found'},
                                status=status.HTTP_404_NOT_FOUND)
            video_record = VideoRecord.objects.filter(master_record=serial,
                                                    season=season,
                                                    episode=episode).first()
            if not video_record:
                return Response({'message': 'Episode not found'},
                                status=status.HTTP_404_NOT_FOUND)
            data = request.data
            video_record.episode = data['new_episode']
            video_record.season = data['new_season']
            video_record.save()
            return Response({'message': 'Episode record updated successfully'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during episode update: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)