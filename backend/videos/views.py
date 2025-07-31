from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status
from secrets import token_urlsafe
from django.db import connection
from PIL import Image

import logging
import json
import os

from .models import (TempVideo, Video, VideoRecord, VideoHistory, VideoGenre, VideoQuery,
                     CustomVideoList, CustomVideoListRecords, VideoFavourites, VideoRequest)
from .queries import (get_video_list_query, get_video_by_genre_query, get_recently_viewed_query,
                      get_video_search_query, get_record_data, video_search_query,
                      get_custom_video_list_records_query, get_favourite_videos_query)

from functions.auth_functions import auth_check
from functions.search_parameters import build_video_query_parameters
from core.serializer import TempVideoSerializer, VideoQuerySerializer, CustomVideoListSerializer

logger = logging.getLogger(__name__)

@api_view(['POST'])
def upload_video(request):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'}, status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            with open('json/directory.json', 'r') as f:
                directory = json.load(f)
            temp_videos_dir = directory['temp_videos_dir']
            os.makedirs(temp_videos_dir, exist_ok=True)
            thumbnail_dir = directory['video_thumbnail_dir']
            os.makedirs(thumbnail_dir, exist_ok=True)
            video_dir = directory['video_dir']
            os.makedirs(video_dir, exist_ok=True)
            serial = None
            while serial is None:
                serial = token_urlsafe(8)
                if TempVideo.objects.filter(serial=serial).exists():
                    serial = None
                if VideoRecord.objects.filter(video_serial=serial).exists():
                    serial = None
            master_serial = None
            while master_serial is None:
                master_serial = token_urlsafe(8)
                if Video.objects.filter(serial=master_serial).exists():
                    master_serial = None
                if TempVideo.objects.filter(master_serial=master_serial).exists():
                    master_serial = None
            video = request.FILES['video']
            video_path = os.path.join(temp_videos_dir, f'{serial}.{video.name.split(".")[-1]}')
            with open(video_path, 'wb+') as f:
                for chunk in video.chunks():
                    f.write(chunk)
            thumbnail = request.FILES.get('thumbnail')
            thumbnail_added = False
            if thumbnail:
                thumbnail_path = os.path.join(thumbnail_dir, f'{serial}.{thumbnail.name.split(".")[-1]}')
                with open(thumbnail_path, 'wb+') as f:
                    for chunk in thumbnail.chunks():
                        f.write(chunk)
                thumbnail_added = True
                image = Image.open(thumbnail_path)
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                image.size = (1280, 720)
                image.save(thumbnail_path, 'JPEG', quality=100, optimize=True)
            private_data = request.data.get('private') == 'true'
            tags = json.loads(request.data.get('tags', '[]'))
            writers = json.loads(request.data.get('writers', '[]'))
            directors = json.loads(request.data.get('directors', '[]'))
            stars = json.loads(request.data.get('stars', '[]'))
            creators = json.loads(request.data.get('creators', '[]'))
            new_temp_video = TempVideo.objects.create(
                video_name=video.name.split('.')[0],
                current_status='U',
                last_updated=timezone.now(),
                title=request.data.get('title'),
                video_location=video_dir,
                thumbnail_location=thumbnail_dir,
                image_added=thumbnail_added,
                imdb_link=request.data.get('imdbLink'),
                tags=tags,
                directors=directors,
                stars=stars,
                writers=writers,
                creators=creators,
                rating=request.data.get('rating'),
                permission=request.data.get('permission'),
                series=False,
                private=private_data,
                uploaded_by=user,
                uploaded_date=timezone.now(),
                season=0,
                episode=0,
                serial=serial,
                master_serial=master_serial,
                temp_video_location=temp_videos_dir,
                temp_video_extension=video.name.split('.')[-1]
            )
            serializer = TempVideoSerializer(new_temp_video)
            return Response({'message': 'Video uploaded successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error during video upload: {str(e)}")
            return Response({'message': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['POST'])
def batch_video_upload(request):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            with open('json/directory.json', 'r') as f:
                directory = json.load(f)
            temp_videos_dir = directory['temp_videos_dir']
            thumbnail_dir = directory['video_thumbnail_dir']
            video_dir = directory['video_dir']
            os.makedirs(temp_videos_dir, exist_ok=True)
            os.makedirs(thumbnail_dir, exist_ok=True)
            os.makedirs(video_dir, exist_ok=True)
            videos = request.FILES.getlist('videos')
            thumbnail_file = request.FILES.get('thumbnail')
            existing_series = request.data.get('existing_series') == 'true'
            master_serial = None
            if existing_series:
                master_serial = request.data.get('master_serial')
                if master_serial:
                    record = TempVideo.objects.filter(master_serial=master_serial).first()
                    if record is None:
                        record = Video.objects.filter(serial=master_serial).first()
                    if record is None:
                        return Response({'message': 'Series with the provided master serial does not exist.'},
                                        status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response({'message': 'Master serial is required for existing series.'},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                while master_serial is None:
                    master_serial = token_urlsafe(8)
                    if TempVideo.objects.filter(master_serial=master_serial).exists() or \
                            Video.objects.filter(serial=master_serial).exists():
                        master_serial = None
            thumbnail_path = None
            image_added = False
            if thumbnail_file:
                thumbnail_extension = thumbnail_file.name.split('.')[-1]
                thumbnail_path = os.path.join(thumbnail_dir, f'{master_serial}.{thumbnail_extension}')
                with open(thumbnail_path, 'wb+') as f:
                    for chunk in thumbnail_file.chunks():
                        f.write(chunk)
                image = Image.open(thumbnail_path)
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                image = image.resize((1280, 720))
                image.save(thumbnail_path, 'JPEG', quality=100, optimize=True)
                image_added = True
            private_data = request.data.get('private_data') == 'true'
            tags = json.loads(request.data.get('tags', '[]'))
            writers = json.loads(request.data.get('writers', '[]'))
            directors = json.loads(request.data.get('directors', '[]'))
            stars = json.loads(request.data.get('stars', '[]'))
            creators = json.loads(request.data.get('creators', '[]'))
            responses = []
            for i, video in enumerate(videos):
                try:
                    serial = None
                    while serial is None:
                        serial = token_urlsafe(8)
                        if TempVideo.objects.filter(serial=serial).exists() or \
                                Video.objects.filter(serial=serial).exists():
                            serial = None
                    video_extension = video.name.split('.')[-1]
                    video_path = os.path.join(temp_videos_dir, f'{serial}.{video_extension}')
                    with open(video_path, 'wb+') as f:
                        for chunk in video.chunks():
                            f.write(chunk)
                    season = request.data.get(f'season_{i}')
                    episode = request.data.get(f'episode_{i}')
                    new_temp_video = TempVideo.objects.create(
                        video_name=video.name.split('.')[0],
                        current_status='U',
                        last_updated=timezone.now(),
                        title=request.data.get('title'),
                        video_location=video_dir,
                        thumbnail_location=thumbnail_dir,
                        image_added=image_added,
                        imdb_link=request.data.get('imdbLink'),
                        tags=tags,
                        directors=directors,
                        stars=stars,
                        writers=writers,
                        creators=creators,
                        rating=request.data.get('rating'),
                        permission=request.data.get('permission'),
                        existing_series=existing_series,
                        series=True,
                        private=private_data,
                        uploaded_by=user,
                        uploaded_date=timezone.now(),
                        season=season,
                        episode=episode,
                        serial=serial,
                        master_serial=master_serial,
                        temp_video_location=temp_videos_dir,
                        temp_video_extension=video_extension
                    )
                    serializer = TempVideoSerializer(new_temp_video)
                    responses.append({
                        'message': f'Video {i + 1} uploaded successfully',
                        'data': serializer.data
                    })
                except Exception as e:
                    logger.error(f"Error during batch video upload: {str(e)}")
                    responses.append({
                        'video_name': video.name,
                        'message': str(e),
                        'status': 'failed'
                    })
            return Response({'message': 'Videos uploaded successfully', 'data': responses},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error during batch video upload: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_series_serials(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            series_serials = Video.objects.filter(
                uploaded_by=user, series=True).values_list('master_serial', flat=True)
            return Response({'message': 'Series serials retrieved successfully',
                             'data': list(series_serials)},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during series serial retrieval: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['GET'])
def get_videos(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            permission = user.permission
            page = int(request.query_params.get('page', 1))
            limit = int(request.query_params.get('limit', 5))
            offset = (page - 1) * limit
            query = get_video_list_query()
            with connection.cursor() as cursor:
                cursor.execute(query, [permission, limit + 1, offset])
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                has_more = len(rows) > limit
                videos = [dict(zip(columns, row)) for row in rows[:limit]]
            return Response({'message': 'Videos retrieved successfully',
                             'data': {'videos': videos, 'has_more': has_more}},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during video retrieval: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_video_thumbnail(request, serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            video = Video.objects.filter(serial=serial).first()
            if video is None:
                return Response({'message': 'Video not found'},
                                status=status.HTTP_404_NOT_FOUND)
            thumbnail_path = video.thumbnail_location + f'{serial}.jpg'
            with open(thumbnail_path, 'rb') as f:
                return HttpResponse(f.read(), content_type='image/jpeg')
        except Exception as e:
            logging.error(f"Error during thumbnail retrieval: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_video_data(request, serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'}, 
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            user_id = user.username
            with connection.cursor() as cursor:
                cursor.execute(get_record_data(), [user_id, user_id,
                                                   user_id, user_id, serial])
                result = cursor.fetchone()
            if not result:
                return Response({'message': 'Video not found'},
                                status=status.HTTP_404_NOT_FOUND)
            columns = [
                'video_name', 'video_directors', 'video_stars', 'video_writers',
                'video_creators', 'video_genres', 'video_description', 'video_rating',
                'resume', 'resume_serial', 'video_serial', 'series', 'season_metadata',
                'serial', 'favourites', 'in_custom_album', 'not_in_custom_album'
            ]
            video_data = dict(zip(columns, result))
            video_data['video_directors'] = video_data['video_directors'].split(
                ', ') if video_data['video_directors'] else []
            video_data['video_stars'] = video_data['video_stars'].split(
                ', ') if video_data['video_stars'] else []
            video_data['video_writers'] = video_data['video_writers'].split(
                ', ') if video_data['video_writers'] else []
            video_data['video_creators'] = video_data['video_creators'].split(
                ', ') if video_data['video_creators'] else []
            video_data['video_genres'] = video_data['video_genres'].split(
                ', ') if video_data['video_genres'] else []
            video_data['season_metadata'] = json.loads(
                video_data['season_metadata']) if video_data['season_metadata'] else {}
            video_data['in_custom_album'] = [
                json.loads(album) for album in video_data['in_custom_album'] if album
            ] if video_data['in_custom_album'] else []
            video_data['not_in_custom_album'] = [
                json.loads(album) for album in video_data['not_in_custom_album'] if album
            ] if video_data['not_in_custom_album'] else []
            return Response(video_data, status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during video data retrieval: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['GET'])
def episode_data(request, serial, season):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            video = Video.objects.filter(serial=serial, uploaded_by_id=user.username).first()
            if not video:
                return Response({'message': 'Video not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            season_data = VideoRecord.objects.filter(master_record=video.serial,
                                                     season=season).values(
                                                         'episode',
                                                         'video_name',
                                                         'video_serial').order_by(
                                                             'episode')
            for episode in season_data:
                history_instance = VideoHistory.objects.filter(
                    serial=episode['video_serial'], user=user.username).exists()
                if history_instance:
                    episode['resume'] = True
                else:
                    episode['resume'] = False
            return Response({'episodes': list(season_data)},
                                status=status.HTTP_200_OK) 
        except Exception as e:
            logging.error(f"Error during video upload: {str(e)}")
            return Response({'message': 'Internal server error'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_genres(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            genres_queryset = VideoGenre.objects.filter(
                number_of_public_records__gte=1).values('genre')
            genres_list = list(genres_queryset)
            return Response({'genres': genres_list},
                                status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during video upload: {str(e)}")
            return Response({'message': 'Internal server error'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['GET'])
def get_videos_by_genre(request, genre):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            permission = user.permission
            page = int(request.query_params.get('page', 1))
            limit = int(request.query_params.get('limit', 5))
            offset = (page - 1) * limit
            query = get_video_by_genre_query()
            with connection.cursor() as cursor:
                cursor.execute(query, [permission, genre, limit + 1, offset])
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                has_more = len(rows) > limit
                videos = [dict(zip(columns, row)) for row in rows[:limit]]
            return Response({
                    'message': 'Videos retrieved successfully',
                    'data': {'videos': videos, 'has_more': has_more}},
                status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during genre video retrieval: {str(e)}")
            return Response(
                {'message': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def recently_viewed_videos(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            user_id = user.username
            permission = user.permission
            query = get_recently_viewed_query()
            page = int(request.query_params.get('page', 1))
            limit = int(request.query_params.get('limit', 5))
            offset = (page - 1) * limit
            with connection.cursor() as cursor:
                cursor.execute(query, [user_id, permission, limit + 1, offset])
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                has_more = len(rows) > limit
                videos = [dict(zip(columns, row)) for row in rows[:limit]]
            return Response({'message': 'Recently viewed videos retrieved successfully',
                             'data': {'videos': videos, 'has_more': has_more}},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during recently viewed video retrieval: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_videos_by_search(request, search):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return auth_response['error']
            user = auth_response['user']
            query = get_video_search_query()
            with connection.cursor() as cursor:
                cursor.execute(query, [f"%{search}%",
                                    ])
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                videos = [dict(zip(columns, row)) for row in rows]
                return Response({'message': 'Search videos retrieved successfully',
                                'data': videos},
                                status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during search video retrieval: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['POST'])
def generate_video_search(request):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return auth_response['error']
            user = auth_response['user']
            user_id = user.username
            search_id = None
            while search_id is None:
                serial = token_urlsafe(8)
                if VideoQuery.objects.filter(query_id=serial).exists():
                    search_id = None
                else:
                    search_id = serial
            query = request.data.get('searchRows')
            exact_genre = []
            similar_genre = []
            exact_star = []
            similar_star = []
            exact_director = []
            similar_director = []
            exact_writer = []
            similar_writer = []
            exact_creator = []
            similar_creator = []
            for row in query:
                if row['searchType'] == 'Genre':
                    if row['matchType'] == 'Exact Match':
                        exact_genre.append(row['query'])
                    elif row['matchType'] == 'Similar Match':
                        similar_genre.append(row['query'])
                elif row['searchType'] == 'Star':
                    if row['matchType'] == 'Exact Match':
                        exact_star.append(row['query'])
                    elif row['matchType'] == 'Similar Match':
                        similar_star.append(row['query'])
                elif row['searchType'] == 'Director':
                    if row['matchType'] == 'Exact Match':
                        exact_director.append(row['query'])
                    elif row['matchType'] == 'Similar Match':
                        similar_director.append(row['query'])
                elif row['searchType'] == 'Writer':
                    if row['matchType'] == 'Exact Match':
                        exact_writer.append(row['query'])
                    elif row['matchType'] == 'Similar Match':
                        similar_writer.append(row['query'])
                elif row['searchType'] == 'Creator':
                    if row['matchType'] == 'Exact Match':
                        exact_creator.append(row['query'])
                    elif row['matchType'] == 'Similar Match':
                        similar_creator.append(row['query'])
                else:
                    return Response({'message': f'Invalid search type, {row["searchType"]} is not valid'},
                                    status=status.HTTP_400_BAD_REQUEST)
                new_video_search = VideoQuery.objects.create(
                    query_id=search_id,
                    video_exact_genre=exact_genre,
                    video_similar_genre=similar_genre,
                    video_exact_stars=exact_star,
                    video_similar_stars=similar_star,
                    video_exact_directors=exact_director,
                    video_similar_directors=similar_director,
                    video_exact_writers=exact_writer,
                    video_similar_writers=similar_writer,
                    video_exact_creators=exact_creator,
                    video_similar_creators=similar_creator,
                    user=user,
                )
                serializer = VideoQuerySerializer(new_video_search)
            return Response({'message': 'Search videos retrieved successfully',
                            'data': search_id},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            logging.error(f"Error during generating video search: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_video_query(request, search_id):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            search = VideoQuery.objects.filter(query_id=search_id, user=user).first()
            if not search:
                return Response({'message': 'Search not found'},
                                status=status.HTTP_404_NOT_FOUND)
            query = video_search_query()
            query_params = build_video_query_parameters(search)
            with connection.cursor() as cursor:
                cursor.execute(query, query_params)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                videos = [dict(zip(columns, row)) for row in rows]
            return Response({
                'message': 'Videos retrieved successfully',
                'data': videos
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during video search retrieval: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def create_custom_video_list(request):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            user_id = user.username
            list_name = request.data.get('list_name')
            list_serial = None
            while list_serial is None:
                serial = token_urlsafe(8)
                if CustomVideoList.objects.filter(
                    list_serial=serial).exists():
                    list_serial = None
                else:
                    list_serial = serial
            new_record = CustomVideoList.objects.create(
                list_name=list_name,
                list_serial=list_serial,
                user=user
            )
            record = CustomVideoListSerializer(new_record)
            return Response({'message': 'Custom video list created successfully'},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            logging.error(f"Error during custom video list creation: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def add_video_to_custom_list(request, video_serial, list_serial):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            user_id = user.username
            list_record = CustomVideoList.objects.filter(
                list_serial=list_serial, user=user).first()
            if not list_record:
                return Response({'message': 'Custom video list not found'},
                                status=status.HTTP_404_NOT_FOUND)
            video_record = Video.objects.filter(serial=video_serial).first()
            if not video_record:
                return Response({'message': 'Video not found'},
                                status=status.HTTP_404_NOT_FOUND)
            new_list_record = CustomVideoListRecords.objects.create(
                list_serial=list_record,
                video_serial=video_record,
                user=user
            )
            new_list_record.save()
            return Response({'message': 'Video added to custom list successfully'},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            logging.error(f"Error during adding video to custom list: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def remove_video_from_custom_list(request, video_serial, list_serial):
    if request.method == 'DELETE':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            user_id = user.username
            list_record = CustomVideoList.objects.filter(
                list_serial=list_serial, user=user).first()
            if not list_record:
                return Response({'message': 'Custom video list not found'},
                                status=status.HTTP_404_NOT_FOUND)
            video_record = Video.objects.filter(serial=video_serial).first()
            if not video_record:
                return Response({'message': 'Video not found'},
                                status=status.HTTP_404_NOT_FOUND)
            list_record = CustomVideoListRecords.objects.filter(
                list_serial=list_record, video_serial=video_record, user=user).first()
            if not list_record:
                return Response({'message': 'Video not found in custom list'},
                                status=status.HTTP_404_NOT_FOUND)
            list_record.delete()
            return Response({'message': 'Video removed from custom list successfully'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during removing video from custom list: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_custom_video_lists(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            records = CustomVideoList.objects.filter(user=user).values('list_name', 'list_serial')
            data = list(records)
            return Response({'message': 'Custom video lists retrieved successfully',
                            'data': data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during custom video list retrieval: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['GET'])
def get_custom_video_list_records(request, list_serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            user_id = user.username
            page = int(request.query_params.get('page', 1))
            limit = int(request.query_params.get('limit', 5))
            offset = (page - 1) * limit
            query = get_custom_video_list_records_query()
            with connection.cursor() as cursor:
                cursor.execute(query, [list_serial, user_id, limit + 1, offset])
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                has_more = len(rows) > limit
                videos = [dict(zip(columns, row)) for row in rows[:limit]]
            return Response({
                'message': 'Custom video list records retrieved successfully',
                'data': {
                    'videos': videos,
                    'has_more': has_more,
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during custom video list records retrieval: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def update_video_favourites(request, serial):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            user_id = user.username
            video = Video.objects.filter(serial=serial).first()
            if not video:
                return Response({'message': 'Video not found'},
                                status=status.HTTP_404_NOT_FOUND)
            if request.data['action'] == 'add':
                new_favourite = VideoFavourites.objects.create(
                    user=user,
                    video=video
                )
                new_favourite.save()
                return Response({'message': 'Video added to favourites successfully'},
                                status=status.HTTP_201_CREATED)
            if request.data['action'] == 'remove':
                favourite = VideoFavourites.objects.filter(user=user, video=video).first()
                if not favourite:
                    return Response({'message': 'Video not found in favourites'},
                                    status=status.HTTP_404_NOT_FOUND)
                favourite.delete()
                return Response({'message': 'Video removed from favourites successfully'},
                                status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during updating video favourites: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_favourite_videos(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            user_id = user.username
            query = get_favourite_videos_query()
            with connection.cursor() as cursor:
                cursor.execute(query, [user_id])
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                videos = [dict(zip(columns, row)) for row in rows]
            return Response({'message': 'Favourite videos retrieved successfully',
                'data': videos
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during favourite video retrieval: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['POST'])
def create_video_request(request):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            new_request = VideoRequest.objects.create(
                user=user,
                request_title=request.data.get('request_title'),
                request_description=request.data.get('request_description')
            )
            new_request.save()    
            return Response({'message': 'Video request created successfully'},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            logging.error(f"Error during video request creation: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_video_requests(request):
    print('get_video_requests')
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            user_requests = VideoRequest.objects.filter(user=user).values(
                'request_title', 'request_description', 'request_date', 'request_status')
            user_requests = list(user_requests)
            if not user_requests:
                return Response({'message': 'No video requests found'},
                                status=status.HTTP_404_NOT_FOUND)
            return Response({'message': 'Video requests retrieved successfully',
                            'data': user_requests},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during video request retrieval: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)