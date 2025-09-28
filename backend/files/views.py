from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse, FileResponse
from django.utils import timezone
from rest_framework import status
from urllib.parse import quote

import zipfile
import logging
import mimetypes
import json
import os

from functions.auth_functions import auth_check
from functions.generate_share_code import generate_share_code
from functions.serial_default_generator import generate_serial_code

from .models import ShareFolder, ShareFile

logger = logging.getLogger(__name__)

@api_view(['POST'])
def create_upload_folder(request):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            serial = generate_serial_code(
                config_section='files',
                serial_key='folder_serial_code',
                model=ShareFolder,
                field_name='serial'
            )
            share_code = generate_share_code()
            new_folder = ShareFolder(
                user=user,
                folder_name=request.data.get('folder_name', 'New Folder'),
                serial=serial,
                share_code=share_code,
                folder_description=request.data.get('folder_description', ''),
                sharable=request.data.get('sharable', False),
                create_date=timezone.now(),
                update_date=timezone.now()
            )
            new_folder.save()
            return Response({'message': 'Folder created successfully'},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error in create_upload_folder: {e}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def upload_file(request):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response(
                    {'message': f'{auth_response["error"]}'},
                    status=status.HTTP_403_FORBIDDEN
                )
            user = auth_response['user']
            serial = generate_serial_code(
                config_section='files',
                serial_key='file_serial_code',
                model=ShareFile,
                field_name='file_serial'
            )
            folder_serial = request.data.get('folder_serial', None)
            with open('json/directory.json', 'r') as f:
                directory = json.load(f)
            file = request.FILES.get('file')
            if not file:
                return Response(
                    {'message': 'No file uploaded'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            file_full_name = file.name
            if '.' in file_full_name:
                file_name, file_extension = file_full_name.rsplit('.', 1)
            else:
                file_name = file_full_name
                file_extension = ''
            if folder_serial:
                added_to_folder = True
            else:
                added_to_folder = False
            file_directory = directory['share_file_upload_dir']
            os.makedirs(file_directory, exist_ok=True)
            file_path = os.path.join(file_directory, f"{serial}.{file_extension}")
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            share_code = generate_share_code()
            new_file = ShareFile(
                user=user,
                file_name=file_name,
                folder_serial=ShareFolder.objects.get(serial=folder_serial) if folder_serial else None,
                file_serial=serial,
                file_description=request.data.get('file_description', ''),
                share_code=share_code,
                added_to_folder=added_to_folder,
                file_location=file_directory,
                file_type=file_extension,
                sharable=request.data.get('sharable', False),
                create_date=timezone.now(),
                update_date=timezone.now()
            )
            new_file.save()
            return Response({'message': 'File uploaded successfully'},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error in upload_file: {e}")
            return Response(
                {'message': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_files(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            files = ShareFile.objects.filter(user=user, added_to_folder=False).values(
                'file_serial', 'file_name', 'file_description', 'file_type', 'sharable')   
            data = {}
            if not files:
                return Response({'message': 'No files found in this folder',
                                 'data': data},
                                status=status.HTTP_200_OK)  
            for file in files:
                data[file['file_serial']] = {
                    'file_name': file['file_name'],
                    'file_description': file['file_description'],
                    'file_type': file['file_type'],
                    'file_share_status': file['sharable']
                }
            print( data)
            return Response({'message': 'Files retrieved successfully',
                            'data': data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in view_files: {e}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_folder_files(request, folder_serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            folder = ShareFolder.objects.filter(serial=folder_serial,
                                                user=user).first()
            files = ShareFile.objects.filter(folder_serial=folder, user=user).values(
                'file_serial', 'file_name', 'file_description', 'file_type', 'sharable')
            data = {}
            if not files:
                return Response({'message': 'No files found in this folder',
                                 'data': {}},
                                status=status.HTTP_200_OK)
            for file in files:
                data[file['file_serial']] = {
                    'file_name': file['file_name'],
                    'file_description': file['file_description'],
                    'file_type': file['file_type'],
                    'file_share_status': file['sharable']
                }
            print(data)
            return Response({'message': 'Files retrieved successfully',
                            'data': data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in view_folder_files: {e}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_folder_data(request, folder_serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            folder = ShareFolder.objects.filter(serial=folder_serial,
                                                user=user).first()
            if not folder:
                return Response({'message': 'Folder not found'},
                                status=status.HTTP_404_NOT_FOUND)
            data = {
                'folder_name': folder.folder_name,
                'folder_description': folder.folder_description,
                'sharable': folder.sharable,
                'create_date': folder.create_date,
                'update_date': folder.update_date
            }
            return Response({'message': 'Folder data retrieved successfully',
                            'data': data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in get_folder_data: {e}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_folders(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            folders = ShareFolder.objects.filter(user=user).values(
                'serial', 'folder_name', 'folder_description',
                'sharable', 'create_date', 'update_date'
            )
            if not folders:
                return Response({'message': 'No folders found'},
                                status=status.HTTP_200_OK)
            data = {}
            for folder in folders:
                data[folder['serial']] = {
                    'folder_name': folder['folder_name'],
                    'folder_description': folder['folder_description'],
                    'sharable': folder['sharable'],
                    'create_date': folder['create_date'],
                    'update_date': folder['update_date']
                }
            return Response({'message': 'Folders retrieved successfully',
                            'data': data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in view_folders: {e}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['GET'])
def get_file(request, file_id):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            file = ShareFile.objects.filter(file_serial=file_id,
                                            user=user).first()
            if not file:
                return Response({'message': 'File not found'},
                                status=status.HTTP_404_NOT_FOUND)
            data = {
                'file_name': file.file_name,
                'file_description': file.file_description,
                'file_type': file.file_type,
                'sharable': file.sharable,
                'added_to_folder': file.added_to_folder,
            }
            return Response({'message': 'File retrieved successfully',
                            'data': data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in view_file: {e}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_downloaded_file(request, file_id, share_code):
    try:
        token = request.headers.get('Authorization')
        auth_response = auth_check(token)
        if 'error' in auth_response:
            return Response(
                {'message': f'{auth_response["error"]}'},
                status=status.HTTP_403_FORBIDDEN
            )
        extension_mime_map = {
            "csv": "text/csv; charset=utf-8",
            "tsv": "text/tab-separated-values; charset=utf-8",
            "json": "application/json; charset=utf-8",
            "txt": "text/plain; charset=utf-8",
        }
        file = ShareFile.objects.filter(
            file_serial=file_id,
            share_code=share_code,
            sharable=True
        ).first()
        if not file:
            return Response(
                {'message': 'File not found'},
                status=status.HTTP_404_NOT_FOUND)
        file_path = os.path.join(
            file.file_location,
            f"{file.file_serial}.{file.file_type}")
        if not os.path.exists(file_path):
            return Response(
                {'message': 'File not found on server'},
                status=status.HTTP_404_NOT_FOUND)
        ext = file.file_type.lower()
        mime_type = extension_mime_map.get(ext)
        if not mime_type:
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = "application/octet-stream"
        response = FileResponse(
            open(file_path, 'rb'),
            content_type=mime_type,
            status=status.HTTP_200_OK)
        response['Content-Disposition'] = (
            f'attachment; filename="{quote(file.file_name)}.{file.file_type}"')
        return response
    except Exception as e:
        logger.error(f"Error in get_downloaded_file: {e}")
        return Response(
            {'message': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_folder_downloaded_files(request, folder_serial, share_code):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            folder = ShareFolder.objects.filter(serial=folder_serial,
                                                share_code=share_code,
                                                sharable=True).first()
            if not folder:
                return Response({'message': 'Folder not found'},
                                status=status.HTTP_404_NOT_FOUND)
            files = ShareFile.objects.filter(folder_serial=folder,
                                             sharable=True).all()
            if not files:
                print('No files found in this folder')
                return Response({'message': 'No files found in this folder'},
                                status=status.HTTP_200_OK)
            for file in files:
                file_path = file.file_location + file.file_serial + '.' + file.file_type
                if not os.path.exists(file_path):
                    return Response({'message': f'File {file.file_name} not found on server'},
                                    status=status.HTTP_404_NOT_FOUND)
            zip_filename = f"{folder_serial}_files.zip"
            with zipfile.ZipFile(zip_filename, 'w') as zipf:
                for file in files:
                    file_path = file.file_location + file.file_serial + '.' + file.file_type
                    zipf.write(file_path, arcname=file.file_name)
            with open(zip_filename, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'
                response['status'] = status.HTTP_200_OK
            os.remove(zip_filename)
            return response
        except Exception as e:
            logger.error(f"Error in get_folder_downloaded_files: {e}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_file_share_data(request, file_id):
    try:
        token = request.headers.get('Authorization')
        auth_response = auth_check(token)
        if 'error' in auth_response:
            return Response({'message': f'{auth_response["error"]}'},
                            status=status.HTTP_403_FORBIDDEN)
        user = auth_response['user']
        file = ShareFile.objects.filter(
            file_serial=file_id, user=user).first()
        if not file:
            return Response({'message': 'File not found',
                             'data':{}},
                            status=status.HTTP_404_NOT_FOUND)
        data = {
            'file_name': file.file_name,
            'file_description': file.file_description,
            'file_type': file.file_type,
            'sharable': file.sharable,
            'added_to_folder': file.added_to_folder,
            'share_code': file.share_code
        }
        return Response({'message': 'File data retrieved successfully',
                         'data': data},
                        status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error in get_file_share_data: {e}")
        return Response({'message': 'Internal server error'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def update_file_share_status(request, file_id):
    if request.method == 'PATCH':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            file = ShareFile.objects.filter(file_serial=file_id, user=user).first()
            if not file:
                return Response({'message': 'File not found'},
                                status=status.HTTP_404_NOT_FOUND)
            file.sharable = request.data.get('sharable', file.sharable)
            file.update_date = timezone.now()
            file.save()
            return Response({'message': 'File share status updated successfully'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in update_file_share_status: {e}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_folder_share_data(request, folder_serial):
    try:
        token = request.headers.get('Authorization')
        auth_response = auth_check(token)
        if 'error' in auth_response:
            return Response({'message': f'{auth_response["error"]}'},
                            status=status.HTTP_403_FORBIDDEN)
        user = auth_response['user']
        folder = ShareFolder.objects.filter(
            serial=folder_serial, user=user).first()
        if not folder:
            return Response({'message': 'Folder not found',
                             'data':{}},
                            status=status.HTTP_404_NOT_FOUND)
        data = {
            'folder_name': folder.folder_name,
            'folder_description': folder.folder_description,
            'sharable': folder.sharable,
            'share_code': folder.share_code,
            'create_date': folder.create_date,
            'update_date': folder.update_date
        }
        return Response({'message': 'Folder data retrieved successfully',
                         'data': data},
                        status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error in get_folder_share_data: {e}")
        return Response({'message': 'Internal server error'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def update_folder_share_status(request, folder_serial):
    if request.method == 'PATCH':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            folder = ShareFolder.objects.filter(serial=folder_serial, user=user).first()
            if not folder:
                return Response({'message': 'Folder not found'},
                                status=status.HTTP_404_NOT_FOUND)
            folder.sharable = request.data.get('sharable', folder.sharable)
            folder.update_date = timezone.now()
            folder.save()
            return Response({'message': 'Folder share status updated successfully'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in update_folder_share_status: {e}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['GET'])
def get_file_share_link(request, file_id):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            file = ShareFile.objects.filter(file_serial=file_id,
                                            user=user).first()
            if not file:
                return Response({'message': 'File not found'},
                                status=status.HTTP_404_NOT_FOUND)
            if not file.sharable:
                return Response({'message': 'File is not sharable'},
                                status=status.HTTP_403_FORBIDDEN)
            share_data = {
                'serial' : file.file_serial,
                'share_code' : file.share_code
            }
            return Response({'message': 'File share link retrieved successfully',
                            'data': share_data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in get_file_share_link: {e}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['GET'])
def get_folder_share_link(request, folder_serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            folder = ShareFolder.objects.filter(serial=folder_serial,
                                                user=user).first()
            if not folder:
                return Response({'message': 'Folder not found'},
                                status=status.HTTP_404_NOT_FOUND)
            if not folder.sharable:
                return Response({'message': 'Folder is not sharable'},
                                status=status.HTTP_403_FORBIDDEN)
            share_data = {
                'serial' : folder.serial,
                'share_code' : folder.share_code
            }
            return Response({'message': 'Folder share link retrieved successfully',
                            'data': share_data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in get_folder_share_link: {e}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def delete_file(request, file_id):
    if request.method == 'DELETE':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            if request.data.get('deletion_confirmation', '') != 'DELETE':
                return Response({'message': 'Deletion confirmation not provided or incorrect'},
                                status=status.HTTP_400_BAD_REQUEST)
            file = ShareFile.objects.filter(file_serial=file_id,
                                            user=user).first()
            if not file:
                return Response({'message': 'File not found'},
                                status=status.HTTP_404_NOT_FOUND)
            file_path = file.file_location + file.file_serial + '.' + file.file_type
            if os.path.exists(file_path):
                os.remove(file_path)
            file.delete()
            return Response({'message': 'File deleted successfully'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in delete_file: {e}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def delete_folder(request, folder_serial):
    if request.method == 'DELETE':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            if request.data.get('deletion_confirmation', '') != 'DELETE':
                return Response({'message': 'Deletion confirmation not provided or incorrect'},
                                status=status.HTTP_400_BAD_REQUEST)
            folder = ShareFolder.objects.filter(serial=folder_serial,
                                                user=user).first()
            if not folder:
                return Response({'message': 'Folder not found'},
                                status=status.HTTP_404_NOT_FOUND)
            folder_files = ShareFile.objects.filter(folder_serial=folder, user=user).all()
            for file in folder_files:
                file_path = file.file_location + file.file_serial + '.' + file.file_type
                if os.path.exists(file_path):
                    os.remove(file_path)
                file.delete()
            folder.delete()
            return Response({'message': 'Folder and its files deleted successfully'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in delete_folder: {e}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)