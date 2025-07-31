from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db import connection
from django.http import FileResponse, JsonResponse
from secrets import token_urlsafe
from PIL import Image, ExifTags

from functions.auth_functions import auth_check
from functions.image_functions import extract_exif_data
from functions.search_parameters import build_picture_query_parameters
from functions.json_formats import json_image_backup, json_album_backup, custom_album_backup, json_revision_format_for_albums
from functions.json_formats import json_revision_format_for_custom_albums, json_revision_format_for_images
from .models import DefaultAlbums, Picture, MyAlbums, MyAlbumPictures, FavouritePictures, ImageTags, ImagePeopleTags, PictureQuery
from .queries import custom_album_data_query, favourite_pictures_query, picture_search_query, picture_data_query
from core.serializer import DefaultAlbumsSerializer, MyAlbumsSerializer, PictureQuerySerializer
from core.fetch_serializer import PictureFetchSerializer, DefaultAlbumFetchSerializer, MyAlbumsFetchSerializer

import logging
import json
import os

logger = logging.getLogger(__name__)

@api_view(['POST'])
def upload_picture(request):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            image = request.FILES.get('image')
            with open('json/directory.json', 'r') as f:
                directory = json.load(f)
            current_album = DefaultAlbums.objects.filter(album_serial=request.data['album']).first()
            if not current_album:
                return Response({'message': 'Album does not exist'},
                                status=status.HTTP_400_BAD_REQUEST)
            image_dir = directory['image_dir']
            image_backup_dir = directory['image_backup_dir']
            os.makedirs(image_dir, exist_ok=True)
            os.makedirs(image_backup_dir, exist_ok=True)
            current_time = timezone.now().strftime('%Y-%m-%d_%H-%M-%S')
            full_backup_path = os.path.join(f'{image_backup_dir}{current_time}')
            os.makedirs(full_backup_path, exist_ok=True)
            unique_token = False
            while not unique_token:
                serial = token_urlsafe(10)
                existing_image = Picture.objects.filter(picture_serial=serial).first()
                if not existing_image:
                    unique_token = True
            exif_dict = extract_exif_data(image)
            user_editable_status = request.data['user_editable'].lower() == 'true'
            json_format = json_image_backup(
                image_name=image.name,
                image_path=image_dir,
                image_extension=image.name.split('.')[-1],
                image_serial=serial,
                image_description=request.data['description'],
                image_upload_time=current_time,
                tags=request.data.getlist('tags')[0].split(','),
                people=request.data.getlist('people')[0].split(','),
                album=request.data['album'],
                uploaded_by=user.username,
                user_editable=user_editable_status,
                status='A',
                originanl_image_extension=image.name.split('.')[-1],
                exif_data=exif_dict
            )
            with open(f'{full_backup_path}/{serial}.json', 'w') as f:
                json.dump(json_format, f, indent=4, ensure_ascii=False)
            image_pathway_backup = f'{full_backup_path}/{serial}.{image.name.split(".")[-1]}'
            with open(image_pathway_backup, 'wb') as f:
                for chunk in image.chunks():
                    f.write(chunk)
            image_pathway_dir = f'{image_dir}/{serial}.png'
            image_original = Image.open(image)
            try:
                for orientation in ExifTags.TAGS.keys():
                    if ExifTags.TAGS[orientation] == 'Orientation':
                        break
                exif = image_original._getexif()
                if exif and orientation in exif:
                    if exif[orientation] == 3:
                        image_original = image_original.rotate(180, expand=True)
                    elif exif[orientation] == 6:
                        image_original = image_original.rotate(270, expand=True)
                    elif exif[orientation] == 8:
                        image_original = image_original.rotate(90, expand=True)
            except (AttributeError, KeyError, IndexError, TypeError):
                pass
            image_original.save(image_pathway_dir, 'PNG', quality=100)
            image_original.close()
            image_thumbnail = Image.open(image_pathway_dir)
            image_thumbnail.thumbnail((300, 300))
            thumbnail_path = f'{directory["image_thumbnail_dir"]}{serial}.jpg'
            os.makedirs(directory['image_thumbnail_dir'], exist_ok=True)
            if image_thumbnail.mode == 'RGBA':
                image_thumbnail = image_thumbnail.convert('RGB')
            image_thumbnail.save(thumbnail_path, 'JPEG', quality=85)
            image_thumbnail.close()
            new_picture = Picture.objects.create(
                picture_serial=serial,
                album=current_album,
                uploaded_by=user,
                picture_pathway=image_dir,
                thumbnail_pathway=directory["image_thumbnail_dir"],
                picture_title=request.data['title'],
                description=request.data['description'],
                picture_editable=user_editable_status,
                picture_name=image.name.split('.')[0],
                full_backup_path=image_pathway_backup,
                original_image_extension=image.name.split('.')[-1],
                current_status='A',
                backup_path=f'{full_backup_path}/',
                album_pathway=current_album.album_pathway
            )
            new_picture.save()
            tags = request.data.getlist('tags')[0].split(',')
            for tag in tags:
                ImageTags.objects.create(
                    picture=new_picture,
                    album=current_album,
                    tag=tag
                )
            people = request.data.getlist('people')[0].split(',')
            for person in people:
                ImagePeopleTags.objects.create(
                    picture=new_picture,
                    album=current_album,
                    person=person
                )
            return Response({'message': 'Image uploaded successfully'},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error during picture upload: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_picture(request, album):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            current_album = DefaultAlbums.objects.filter(album_serial=album).first()
            if not current_album:
                return Response({'message': 'Album does not exist'},
                                status=status.HTTP_400_BAD_REQUEST)
            pictures = Picture.objects.filter(album=current_album,
                                            current_status='A').all()
            data = PictureFetchSerializer(pictures, many=True).data
            return Response({'data': data},
                            status=status.HTTP_200_OK)       
        except Exception as e:
            logger.error(f"Error during picture retrieval: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_tags(request, album_id):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            current_album = DefaultAlbums.objects.filter(album_serial=album_id).first()
            if not current_album:
                return Response({'message': 'Album does not exist'},
                                status=status.HTTP_400_BAD_REQUEST)
            tags = current_album.album_data
            return Response({'tags': tags},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during tag retrieval: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def update_picture(request, serial):
    if request.method == 'PATCH':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return auth_response['error']
            picture_record = Picture.objects.filter(picture_serial=serial).first()
            if not picture_record:
                return Response({'message': 'Image does not exist'},
                                status=status.HTTP_400_BAD_REQUEST)
            changed_title = None
            if picture_record.picture_title != request.data['title']:
                changed_title = request.data['title']
            changed_description = None
            if picture_record.description != request.data['description']:
                changed_description = request.data['description']   
            changed_tags = None
            if picture_record.picture_tags != request.data['tags']:
                changed_tags = request.data['tags']
            changed_people = None
            if picture_record.picture_people != request.data['people']:
                changed_people = request.data['people']
            changed_status = None
            if picture_record.current_status != request.data['status']:
                changed_status = request.data['status']
            picture_record.picture_title = request.data['title']
            picture_record.description = request.data['description']
            picture_record.picture_tags = request.data['tags']
            picture_record.picture_people = request.data['people']
            picture_record.current_status = request.data['status']
            picture_record.save()
            current_tags = ImageTags.objects.filter(picture=picture_record).all()
            new_tags = list(request.data['tags'])
            for tag in current_tags:
                if tag.tag not in new_tags:
                    tag.delete()
            for tag in new_tags:
                if tag not in [tag.tag for tag in current_tags]:
                    new_tag = ImageTags.objects.create(
                        picture=picture_record,
                        tag=tag
                    )
                    new_tag.save()
            current_people = ImagePeopleTags.objects.filter(picture=picture_record).all()
            new_people = list(request.data['people'])
            for person in current_people:
                if person.person not in new_people:
                    person.delete()
            for person in new_people:
                if person not in [person.person for person in current_people]:
                    new_person = ImagePeopleTags.objects.create(
                        picture=picture_record,
                        person=person
                    )
                    new_person.save()
            new_update = json_revision_format_for_images(
                title=changed_title,
                description=changed_description,
                tags=changed_tags,
                people=changed_people,
                status=changed_status
            )
            with open(f'{picture_record.full_backup_path}{serial}.json', 'r') as f:
                picture_data = json.load(f)
            picture_data['Revision History'][timezone.now().isoformat()] = new_update
            with open(f'{picture_record.full_backup_path}{serial}.json', 'w') as f:
                json.dump(picture_data, f, indent=4, ensure_ascii=False)
            return Response({'message': 'Image updated successfully'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during picture update: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['GET'])
def get_thumbnail_image(request, serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': 'Image does not exist'},
                                status=status.HTTP_403_FORBIDDEN)
            image = Picture.objects.filter(picture_serial=serial).first()
            if not image:
                return Response({'message': 'Image does not exist'},
                                status=status.HTTP_403_FORBIDDEN)
            thumbnail_path = os.path.join(image.thumbnail_pathway, f'{serial}.jpg')
            if not os.path.exists(thumbnail_path):
                return Response({'message': 'Thumbnail not found'},
                                status=status.HTTP_404_NOT_FOUND)
            return FileResponse(open(thumbnail_path, 'rb'),
                                content_type='image/jpeg',
                                status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during thumbnail retrieval: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_picture_image(request, serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': 'Image does not exist'},
                                status=status.HTTP_403_FORBIDDEN)
            image = Picture.objects.filter(picture_serial=serial).first()
            if not image:
                return Response({'message': 'Image does not exist'},
                                status=status.HTTP_403_FORBIDDEN)
            image_path = os.path.join(image.picture_pathway, f'{serial}.png')
            if not os.path.exists(image_path):
                return Response({'message': 'Image not found'},
                                status=status.HTTP_404_NOT_FOUND)
            return FileResponse(open(image_path, 'rb'),
                                content_type=f'image/png',
                                status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during image retrieval: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_picture_data(request, serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            user_id = user.username
            query = picture_data_query()
            with connection.cursor() as cursor:
                cursor.execute(query, [user_id, user_id, serial])
                data = cursor.fetchall()
                if not data:
                    return Response({'data': {}},
                                    status=status.HTTP_200_OK)
                columns = [col[0] for col in cursor.description]
                data = dict(zip(columns, data[0]))
                return JsonResponse({'data': data},
                                    status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during image info retrieval: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def create_album(request):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            unique_token = False
            while unique_token == False:
                serial = token_urlsafe(10)
                existing_album = DefaultAlbums.objects.filter(album_serial=serial).first()
                if not existing_album:
                    unique_token = True
                    continue
                else:
                    continue
            with open('json/directory.json', 'r') as f:
                directory = json.load(f)
            album_dir = directory['album_backup_dir']
            os.makedirs(album_dir, exist_ok=True)
            date_created = timezone.now().isoformat()
            json_format = json_album_backup(album_name=request.data['album_name'],
                                            album_serial=serial,
                                            album_description=request.data['album_description'],
                                            album_status='A',
                                            album_tags=request.data['tags'],
                                            date_created=date_created
                                            )
            with open(f'{album_dir}/{serial}.json', 'w') as f:
                json.dump(json_format, f, indent=4, ensure_ascii=False)
            new_album = DefaultAlbums.objects.create(
                album_name=request.data['album_name'],
                album_serial=serial,
                album_description=request.data['album_description'],
                user=user,
                album_status='A',
                album_data=request.data['tags'],
                album_pathway=album_dir
            )
            record = DefaultAlbumsSerializer(new_album)
            return Response({'message': 'Album created successfully'},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            logging.error(f"Error during album upload: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_albums(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            all_albums = DefaultAlbums.objects.filter(album_status='A').all()
            data = DefaultAlbumFetchSerializer(all_albums, many=True).data
            return Response({'data': data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during album retrieval: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['PATCH'])
def update_album(request, serial):
    if request.method == 'PATCH':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            album_record = DefaultAlbums.objects.filter(album_serial=serial).first()
            if not album_record:
                return Response({'message': 'Album does not exist'},
                                status=status.HTTP_400_BAD_REQUEST)
            changed_album_name = None
            if album_record.album_name != request.data['album_name']:
                changed_album_name = request.data['album_name']
            changed_album_description = None
            if album_record.album_description != request.data['album_description']:
                changed_album_description = request.data['album_description']
            changed_album_status = None
            if album_record.album_status != request.data['album_status']:
                changed_album_status = request.data['album_status']
            changed_album_tags = None
            if album_record.album_data != request.data['tags']:
                changed_album_tags = request.data['tags']
            album_record.album_name = request.data['album_name']
            album_record.album_description = request.data['album_description']
            album_record.album_status = request.data['album_status']
            album_record.album_data = request.data['tags']
            album_record.save()
            updated_album = json_revision_format_for_albums(
                album_name=changed_album_name,
                album_description=changed_album_description,
                album_tags=changed_album_tags,
                album_status=changed_album_status
            )
            with open(f'{album_record.album_pathway}{album_record.album_serial}.json', 'r') as f:
                album_data = json.load(f)
            album_data['Revision History'][timezone.now().isoformat()] = updated_album
            with open(f'{album_record.album_pathway}{album_record.album_serial}.json', 'w') as f:
                json.dump(album_data, f, indent=4, ensure_ascii=False)
            return Response({'message': 'Album updated successfully'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during album update: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['POST'])
def create_custom_image_album(request):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            unique_token = False
            with open('json/directory.json', 'r') as f:
                directory = json.load(f)
            album_dir = directory['custom_album_backup_dir']
            os.makedirs(album_dir, exist_ok=True)
            while unique_token == False:
                serial = token_urlsafe(10)
                existing_album = MyAlbums.objects.filter(album_serial=serial).first()
                if not existing_album:
                    unique_token = True
                    continue
                else:
                    continue
            new_album = MyAlbums.objects.create(
                user=user,
                album_name=request.data['album_name'],
                album_serial=serial,
                album_description=request.data['album_description'],
                album_status='A',
                album_pathway=album_dir
            )
            new_record = MyAlbumsSerializer(new_album)
            json_format = custom_album_backup(
                creator=user.username,
                album_name=request.data['album_name'],
                album_serial=serial,
                album_description=request.data['album_description'],
                album_status='A',
                album_data={},
                date_created=timezone.now().isoformat()
            )
            with open(f'{album_dir}/{serial}.json', 'w') as f:
                json.dump(json_format, f, indent=4, ensure_ascii=False)
            return Response({'message': 'Custom album created successfully'},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            logging.error(f"Error during custom album creation: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['POST'])
def add_image_to_custom_album(request, album_serial, image_serial):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            user_id = user.username
            picture = Picture.objects.filter(picture_serial=image_serial).first()
            if not picture:
                return Response({'message': 'Image does not exist'},
                                status=status.HTTP_400_BAD_REQUEST)
            album = MyAlbums.objects.filter(album_serial=album_serial, user=user_id).first()
            if not album:
                return Response({'message': 'Album does not exist'},
                                status=status.HTTP_400_BAD_REQUEST)
            album_file = f'{album.album_pathway}{album.album_serial}.json'
            with open(album_file, 'r') as f:
                album_data = json.load(f)
            image = Picture.objects.filter(picture_serial=image_serial).first()
            if not image:
                return Response({'message': 'Image does not exist'},
                                status=status.HTTP_400_BAD_REQUEST)
            new_record = MyAlbumPictures.objects.create(
                album=album,
                picture=image
            )
            new_record.save()
            album_data['Image Entries'].append(image.picture_serial)
            with open(album_file, 'w') as f:
                json.dump(album_data, f, indent=4, ensure_ascii=False)
            return Response({'message': 'Image added to custom album successfully'},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            logging.error(f"Error during adding image to custom album: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_custom_image_album(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            all_albums = MyAlbums.objects.filter(user=user).all()
            data = MyAlbumsFetchSerializer(all_albums, many=True).data
            return Response({'data': data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during custom album retrieval: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_custom_album_images(request, serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            existing_album = MyAlbums.objects.filter(album_serial=serial).first()
            if not existing_album:
                return Response({'message': 'Album does not exist'},
                                status=status.HTTP_400_BAD_REQUEST)
            query = custom_album_data_query()
            with connection.cursor() as cursor:
                cursor.execute(query, [serial])
                data = cursor.fetchall()
                if not data:
                    return Response({'data': []},
                                    status=status.HTTP_200_OK)
                columns = [col[0] for col in cursor.description]
                data = [dict(zip(columns, row)) for row in data]
                return JsonResponse({'data': data},
                                    status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during custom album image retrieval: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def update_custom_image_album(request, serial):
    if request.method == 'PATCH':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            custom_album = MyAlbums.objects.filter(album_serial=serial,
                                                   user=user).first()
            if not custom_album:
                return Response({'message': 'Album does not exist'},
                                status=status.HTTP_400_BAD_REQUEST)
            changed_album_name = None
            if custom_album.album_name != request.data['album_name']:
                changed_album_name = request.data['album_name']
            changed_album_description = None
            if custom_album.album_description != request.data['album_description']:
                changed_album_description = request.data['album_description']
            changed_album_status = None
            if custom_album.album_status != request.data['album_status']:
                changed_album_status = request.data['album_status']
            custom_album.album_name = request.data['album_name']
            custom_album.album_description = request.data['album_description']
            custom_album.album_status = request.data['album_status']
            custom_album.save()
            revision = json_revision_format_for_custom_albums(
                album_name=changed_album_name,
                album_description=changed_album_description,
                album_status=changed_album_status
            )
            with open(f'{custom_album.album_pathway}{custom_album.album_serial}.json', 'r') as f:
                album_data = json.load(f)
            album_data['Revision History'][timezone.now().isoformat()] = revision
            with open(f'{custom_album.album_pathway}{custom_album.album_serial}.json', 'w') as f:
                json.dump(album_data, f, indent=4, ensure_ascii=False)
            return Response({'message': 'Custom album updated successfully'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during custom album update: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['POST'])
def update_image_favourites(request, serial):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            picture = Picture.objects.filter(picture_serial=serial).first()
            if not picture:
                return Response({'message': 'Image does not exist'},
                                status=status.HTTP_400_BAD_REQUEST)
            if request.data['action'] == 'add': 
                serial = None
                while not serial:
                    serial = token_urlsafe(10)
                    existing_favourite = FavouritePictures.objects.filter(serial=serial).first()
                    if existing_favourite:
                        serial = None
                new_favourite = FavouritePictures.objects.create(
                    user=user,
                    picture=picture,
                    serial=serial
                )
                new_favourite.save()
                return Response({'message': 'Image added to favourites successfully'},
                                status=status.HTTP_201_CREATED)
            if request.data['action'] == 'remove':
                favourite_record = FavouritePictures.objects.filter(user=user,
                                                                    picture=picture).first()
                if not favourite_record:
                    return Response({'message': 'Image not in favourites'},
                                    status=status.HTTP_400_BAD_REQUEST)
                favourite_record.delete()
                return Response({'message': 'Image removed from favourites successfully'},
                                status=status.HTTP_200_OK)
            return Response({'message': 'Image added to favourites successfully'},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            logging.error(f"Error during adding to favourites: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['GET'])
def get_image_favourites(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            user_id = user.username
            query = favourite_pictures_query()
            with connection.cursor() as cursor:
                cursor.execute(query, [user_id])
                data = cursor.fetchall()
                if not data:
                    return Response({'data': []},
                                    status=status.HTTP_200_OK)
                columns = [col[0] for col in cursor.description]
                data = [dict(zip(columns, row)) for row in data]
            return JsonResponse({'data': data},
                                status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during favourites retrieval: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def remove_from_image_favourites(request, serial):
    if request.method == 'DELETE':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            image_record = Picture.objects.filter(picture_serial=serial).first()
            if not image_record:
                return Response({'message': 'Image does not exist'},
                                status=status.HTTP_400_BAD_REQUEST)
            favourite_record = FavouritePictures.objects.filter(user=user,
                                                                picture=image_record).first()
            if not favourite_record:
                return Response({'message': 'Image not in favourites'},
                                status=status.HTTP_400_BAD_REQUEST)
            favourite_record.delete()
            return Response({'message': 'Image removed from favourites successfully'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during removing from favourites: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def remove_from_custom_image_album(request, album_serial, image_serial):
    if request.method == 'DELETE':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            user_id = user.username
            image_record = Picture.objects.filter(picture_serial=image_serial).first()
            if not image_record:
                return Response({'message': 'Image does not exist'},
                                status=status.HTTP_400_BAD_REQUEST)
            album_record = MyAlbums.objects.filter(album_serial=album_serial, user=user_id).first()
            if not album_record:
                return Response({'message': 'Album does not exist'},
                                status=status.HTTP_400_BAD_REQUEST)
            album_file = f'{album_record.album_pathway}{album_record.album_serial}.json'
            with open(album_file, 'r') as f:
                album_data = json.load(f)
            if image_serial not in album_data['Image Entries']:
                return Response({'message': 'Image not in album'},
                                status=status.HTTP_400_BAD_REQUEST)
            custom_picture = MyAlbumPictures.objects.filter(album=album_record,
                                                           picture=image_record).first()
            if not custom_picture:
                return Response({'message': 'Image not in album'},
                                status=status.HTTP_400_BAD_REQUEST)
            album_data['Image Entries'].remove(image_serial)
            with open(album_file, 'w') as f:
                json.dump(album_data, f, indent=4, ensure_ascii=False)
            custom_picture.delete()
            return Response({'message': 'Image removed from custom album successfully'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during custom album removal: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def generate_picture_query(request):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            query = request.data.get('searchRows', [])
            if not query:
                return Response({'message': 'searchRows is required and cannot be empty'},
                                status=status.HTTP_400_BAD_REQUEST)
            exact_tags = []
            similar_tags = []
            exact_people = []
            similar_people = []
            for row in query:
                if row['searchType'] == 'Tags':
                    if row['matchType'] == 'Exact Match':
                        exact_tags.append(row['query'])
                    elif row['matchType'] == 'Similar Match':
                        similar_tags.append(row['query'])
                    else:
                        return Response({'message': f'Invalid matchType: {row["matchType"]}'},
                                        status=status.HTTP_400_BAD_REQUEST)
                elif row['searchType'] == 'People':
                    if row['matchType'] == 'Exact Match':
                        exact_people.append(row['query'])
                    elif row['matchType'] == 'Similar Match':
                        similar_people.append(row['query'])
                    else:
                        return Response({'message': f'Invalid matchType: {row["matchType"]}'},
                                        status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'message': f'Invalid searchType: {row["searchType"]}'},
                                    status=status.HTTP_400_BAD_REQUEST)
            search_id = None
            while search_id is None:
                serial = token_urlsafe(8)
                if not PictureQuery.objects.filter(query_id=serial).exists():
                    search_id = serial
            if not search_id:
                logging.error("Failed to generate a unique query_id after multiple attempts")
                return Response({'message': 'Failed to generate a unique query ID'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            new_picture_search = PictureQuery.objects.create(
                user=user,
                query_id=search_id,
                picture_exact_tags=exact_tags,
                picture_similar_tags=similar_tags,
                picture_exact_people=exact_people,
                picture_similar_people=similar_people
            )
            serializer = PictureQuerySerializer(new_picture_search)
            return Response({'message': 'Image query generated successfully',
                             'data': search_id},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            logging.error(f"Error during image query generation: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_picture_query(request, search_id):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            search = PictureQuery.objects.filter(query_id=search_id, user=user).first()
            if not search:
                return Response({'message': 'Query does not exist'},
                                status=status.HTTP_404_NOT_FOUND)
            query = picture_search_query()
            query_params = build_picture_query_parameters(search)
            with connection.cursor() as cursor:
                cursor.execute(query, query_params)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                pictures = [dict(zip(columns, row)) for row in rows]
            return Response({'message': 'Pictures retrieved successfully',
                             'data': pictures},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error during image query retrieval: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)