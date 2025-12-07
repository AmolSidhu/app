from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from django.db import connection
from datetime import datetime
from secrets import token_hex

import hashlib
import logging
import json

from .queries import get_uploaded_video_record_query, picture_upload_data_query
from functions.auth_functions import auth_check, token_generator
from functions.json_formats import json_revision_format_for_images
from videos.models import Video, VideoRecord, VideoTags, VideoDirectors, VideoStars, VideoWriters, VideoCreators
from pictures.models import Picture, ImageTags, ImagePeopleTags
from user.models import Credentials

logger = logging.getLogger(__name__)

@api_view(['POST'])
def import_identifier_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            data = data['data']
            with open('json/directory.json', 'r') as f:
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
            if not video_record or video_record.uploaded_by != user.username:
                return Response({'message': 'Video not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            video_record.update_series = False
            video_record.save()
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
            return Response({'message': 'Episode record updated successfully'},
                                status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error during video upload: {str(e)}")
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
            logger.error(f"Error during video upload: {str(e)}")
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
def change_password(request):
    if request.method == 'PATCH':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            data = request.data
            current_password_hashed = hashlib.sha256(data['current_password'].encode()).hexdigest()
            if current_password_hashed != user.password:
                return Response({'message': 'Incorrect current password'},
                                    status=status.HTTP_400_BAD_REQUEST)
            if data['new_password'] != data['confirm_new_password']:
                return Response({'message': 'New password and confirmation do not match'},
                                    status=status.HTTP_400_BAD_REQUEST)
            new_password_hashed = hashlib.sha256(data['new_password'].encode()).hexdigest()
            user.password = new_password_hashed
            user.save()
            return Response({'message': 'Password changed successfully'},
                                status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during password change: {str(e)}")
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
def get_editing_video_list(request):
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
                                    'uploaded_date': video.uploaded_date,
                                    'status': video.current_status})
            return Response({'data': video_list},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during video list retrieval: {str(e)}")
            return Response({'message': 'Internal server error'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['GET'])
def get_single_video_record(request, serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            query = get_uploaded_video_record_query()
            with connection.cursor() as cursor:
                cursor.execute(query, [serial, user.username])
                columns = [col[0] for col in cursor.description]
                video_data = cursor.fetchone()
            if not video_data:
                return Response({'message': 'Video not found'},
                                status=status.HTTP_404_NOT_FOUND)
            data = dict(zip(columns, video_data))
            print(data)
            return Response({'data': data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during video data request: {str(e)}")
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
            if not video:
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
            print(video_data)
            return Response({'data': video_data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during episode data request: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['GET'])
def get_picture_record(request, serial):
    if request.method == 'GET':
        try:
            picture = Picture.objects.filter(picture_serial=serial).first()
            if not picture:
                return Response({'message': 'Picture not found'},
                                status=status.HTTP_404_NOT_FOUND)
            query = picture_upload_data_query()
            with connection.cursor() as cursor:
                cursor.execute(query, [serial])
                picture_data = cursor.fetchone()
                if not picture_data:
                    return Response({'message': 'Picture data not found'},
                                    status=status.HTTP_404_NOT_FOUND)
                columns = [col[0] for col in cursor.description]
                data = dict(zip(columns, picture_data))
                print(data)
            return Response({'data': data}, status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during picture data request: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['PATCH'])
def update_picture_record(request, serial):
    print(request.data)
    if request.method == 'PATCH':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            picture = Picture.objects.filter(picture_serial=serial).first()
            if not picture:
                return Response({'message': 'Picture not found'},
                                status=status.HTTP_404_NOT_FOUND)
            data = request.data
            updated_description = None
            updated_title = None
            if data.get('picture_description') != picture.description:
                updated_description = data.get('picture_description')
            if data.get('picture_title') != picture.picture_title:
                updated_title = data.get('picture_title')
            picture.description = data['picture_description']
            picture.picture_title = data['picture_title']
            picture.last_updated = datetime.now()
            picture.last_updated_by = user
            picture.save()
            picture_tags = ImageTags.objects.filter(picture=picture).all()
            picture_people = ImagePeopleTags.objects.filter(picture=picture).all()
            current_tags = list(picture_tags.values_list('tag', flat=True))
            current_people = list(picture_people.values_list('person', flat=True))
            new_tags = data.get('tags', [])
            new_people = data.get('people', [])
            for tag in new_tags:
                if tag not in current_tags:
                    ImageTags.objects.create(picture=picture,
                                             album=picture.album,
                                             tag=tag)
            for person in new_people:
                if person not in current_people:
                    ImagePeopleTags.objects.create(
                        picture=picture,
                        album=picture.album,
                        person=person)
            for tag in current_tags:
                if tag not in new_tags:
                    ImageTags.objects.filter(
                        picture=picture,
                        album=picture.album,
                        tag=tag).delete()
            for person in current_people:
                if person not in new_people:
                    ImagePeopleTags.objects.filter(
                        picture=picture,
                        album=picture.album,
                        person=person).delete()
            revision = json_revision_format_for_images(
                title=updated_title,
                description=updated_description,
                tags=new_tags,
                people=new_people,
                status=picture.current_status
            )
            json_file = picture.backup_path + picture.picture_serial + '.json'
            try:
                with open(json_file, 'r') as f:
                    json_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                json_data = {}
            if 'Revision History' not in json_data:
                json_data['Revision History'] = {}
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            json_data['Revision History'][timestamp] = revision
            with open(json_file, 'w') as f:
                json.dump(json_data, f, indent=4)
            print('finished')
            return Response({'message': 'Picture record updated successfully'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during picture update: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def update_video_record(request, serial):
    print('received')
    if request.method == 'PATCH':
        print(request.data)
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            video = Video.objects.filter(serial=serial, uploaded_by=user).first()
            if not video:
                return Response({'message': 'Video not found'},
                                status=status.HTTP_404_NOT_FOUND)
            data = request.data
            video.title = data['title']
            video.description = data['description']
            video.last_updated = datetime.now()
            video.save()
            video_directors = VideoDirectors.objects.filter(video=video).all()
            video_stars = VideoStars.objects.filter(video=video).all()
            video_writers = VideoWriters.objects.filter(video=video).all()
            video_creators = VideoCreators.objects.filter(video=video).all()
            video_tags = VideoTags.objects.filter(video=video).all()
            current_directors = video_directors.values_list('director', flat=True)
            current_stars = video_stars.values_list('star', flat=True)
            current_writers = video_writers.values_list('writer', flat=True)
            current_creators = video_creators.values_list('creator', flat=True)
            current_tags = video_tags.values_list('tag', flat=True)
            new_directors = [director.strip() for director in data.get(
                'directors', '').split(',') if director.strip()]
            new_stars = [star.strip() for star in data.get(
                'stars', '').split(',') if star.strip()]
            new_writers = [writer.strip() for writer in data.get(
                'writers', '').split(',') if writer.strip()]
            new_creators = [creator.strip() for creator in data.get(
                'creators', '').split(',') if creator.strip()]
            new_tags = [tag.strip() for tag in data.get(
                'tags', '').split(',') if tag.strip()]
            for director in new_directors:
                if director not in current_directors:
                    VideoDirectors.objects.create(
                        video=video,
                        director=director)
            for star in new_stars:
                if star not in current_stars:
                    VideoStars.objects.create(
                        video=video,
                        star=star)
            for writer in new_writers:
                if writer not in current_writers:
                    VideoWriters.objects.create(
                        video=video,
                        writer=writer)
            for creator in new_creators:
                if creator not in current_creators:
                    VideoCreators.objects.create(
                        video=video,
                        creator=creator)
            for tag in new_tags:
                if tag not in current_tags:
                    VideoTags.objects.create(
                        video=video,
                        tag=tag)
            for director in current_directors:
                if director not in new_directors:
                    VideoDirectors.objects.filter(
                        video=video,
                        director=director).delete()
            for star in current_stars:
                if star not in new_stars:
                    VideoStars.objects.filter(
                        video=video,
                        star=star).delete()
            for writer in current_writers:
                if writer not in new_writers:
                    VideoWriters.objects.filter(
                        video=video,
                        writer=writer).delete()
            for creator in current_creators:
                if creator not in new_creators:
                    VideoCreators.objects.filter(
                        video=video,
                        creator=creator).delete()
            for tag in current_tags:
                if tag not in new_tags:
                    VideoTags.objects.filter(
                        video=video,
                        tag=tag).delete()
            return Response({'message': 'Video record updated successfully'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during video update: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def update_video_episode(request, serial):
    if request.method == 'PATCH':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            video = Video.objects.filter(serial=serial, uploaded_by=user).first()
            if not video:
                return Response({'message': 'Video not found'},
                                status=status.HTTP_404_NOT_FOUND)
            data = request.data
            video_record = VideoRecord.objects.filter(master_record=serial,
                                                    season=data['current_season'],
                                                    episode=data['current_episode'],
                                                    video_serial=data['video_serial']).first()
            if not video_record:
                return Response({'message': 'Episode not found'},
                                status=status.HTTP_404_NOT_FOUND)
            video_record.episode = data['new_episode']
            video_record.season = data['new_season']
            video_record.last_updated = datetime.now()
            video_record.save()
            video.update_series = False
            video.last_updated = datetime.now()
            video.save()
            return Response({'message': 'Episode record updated successfully'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during episode update: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_server_metadata(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            with open('json/meta.json', 'r') as f:
                directory = json.load(f)
            data = directory
            return Response({'data': data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during server metadata retrieval: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_server_patch_data(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            with open('json/patch.json', 'r') as f:
                directory = json.load(f)
            data = directory
            return Response({'data': data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during server patch data retrieval: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_homepage_video_data(request):
    if request.method == 'GET':
        try:
            pass
        except Exception as e:
            logging.error(f"Error during homepage video data retrieval: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['GET'])
def get_homepage_picture_data(request):
    if request.method == 'GET':
        try:
            pass
        except Exception as e:
            logging.error(f"Error during homepage picture data retrieval: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

