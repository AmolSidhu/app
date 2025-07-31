from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status
from secrets import token_urlsafe
from django.db.models import Max

import re
import logging
import json
import os

from functions.auth_functions import auth_check
from functions.serial_default_generator import serial_default_generator, generate_serial_code

from .models import ShareFolder, ShareFile
from user.models import Credentials

logger = logging.getLogger(__name__)
            
@api_view(['POST'])
def create_upload_folder(request):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            new_serial = generate_serial_code(
                config_section="files",
                serial_key="folder_serial_code",
                model=ShareFolder,
                field_name="serial"
            )
            if not new_serial:
                return Response(
                    {"message": "Serial code generation failed"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            new_record = ShareFolder(
                user=user,
                folder_name=request.data.get('folder_name', 'New Folder'),
                serial=new_serial,
                folder_description=request.data.get('folder_description', 'New Folder'),
                sharable=False
            )
            new_record.save()
            return Response({
                "message": "Upload folder created successfully"
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creating upload folder: {e}")
            return Response(
                {"message": "Failed to create upload folder"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def upload_file(request):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            with open('json/serial_codes.json', 'r') as file:
                serial_codes = json.load(file)
            prefix = serial_codes['files']['file_serial_code'].split('-')[0]
            default_codes = serial_codes['default_codes']
            latest_serial = ShareFile.objects.filter(
                file_serial__startswith=prefix).aggregate(
                Max('file_serial'))['file_serial__max']
            if latest_serial:
                match = re.search(rf"{prefix}-(\d+)", latest_serial)
                if match:
                    current_num = int(match.group(1))
                    new_num = current_num + 1
                    num_len = len(match.group(1))
                else:
                    new_num = 1
                    num_len = len(serial_codes['files']['file_serial_code'].split('-')[1])
            else:
                num_len = len(serial_codes['files']['file_serial_code'].split('-')[1])
                new_num = int(serial_default_generator(
                    default_codes, serial_codes['files']['file_serial_code']))
            new_serial = f"{prefix}-{str(new_num).zfill(num_len)}"
            if not user:
                return Response({"message": "User not found"},
                                status=status.HTTP_404_NOT_FOUND)
            new_record = ShareFile(
                user=user,
                file_name=request.data.get('file_name', 'New File'),
                file_serial=new_serial,
                file_description=request.data.get('file_description', ''),
                sharable=False
            )
            new_record.save()
            return Response({"message": "File uploaded successfully"},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return Response({"message": "Failed to upload file"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['PATCH'])
def update_file_share_status(request, serial):
    if request.method == 'PATCH':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            current_file = ShareFile.objects.get(file_serial=serial,
                                                 user=auth['user']).first()
            if not current_file:
                return Response({"message": "File not found"},
                                status=status.HTTP_404_NOT_FOUND)
            current_file.sharable = request.data.get('sharable', current_file.sharable)
            current_file.save()
            return Response({"message": "Share status updated successfully"},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error updating share status: {e}")
            return Response({"message": "Failed to update share status"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def update_folder_share_status(request, folder_serial):
    if request.method == 'PATCH':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            current_folder = ShareFolder.objects.get(folder_serial=folder_serial,
                                                     user=auth['user']).first()
            if not current_folder:
                return Response({"message": "Folder not found"},
                                status=status.HTTP_404_NOT_FOUND)
            current_folder.sharable = request.data.get('sharable', current_folder.sharable)
            current_folder.save()
            return Response({"message": "Folder share status updated successfully"},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error updating folder share status: {e}")
            return Response({"message": "Failed to update folder share status"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['GET'])
def get_my_shared_files(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
        except Exception as e:
            logger.error(f"Error getting shared files: {e}")
            return Response({"message": "Failed to get shared files"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['PATCH'])
def generate_or_fetch_download_link(request, serial, condition):
    if request.method == 'PATCH':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            if condition == 'folder':
                current_folder = ShareFolder.objects.get(folder_serial=serial,
                                                         user=auth['user']).first()
                if not current_folder:
                    return Response({"message": "Folder not found"},
                                    status=status.HTTP_404_NOT_FOUND)
                current_folder.sharable = True
                current_folder.save()
            if condition == 'file':
                current_file = ShareFile.objects.get(file_serial=serial,
                                                     user=auth['user']).first()
                if not current_file:
                    return Response({"message": "File not found"},
                                    status=status.HTTP_404_NOT_FOUND)
                current_file.sharable = True
                current_file.save()
            else:
                return Response({"message": "Invalid condition"},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "Share link generated successfully"},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error generating or fetching share link: {e}")
            return Response({"message": "Failed to generate or fetch share link"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['GET'])
def view_file(request, file_id):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            current_file = ShareFile.objects.get(file_serial=file_id,
                                                 user=auth['user']).first()
            file = f'{current_file.file_location}{current_file.file_serial}.{current_file.file_type}'
            if not os.path.exists(file):
                return Response({"message": "File not found"},
                                status=status.HTTP_404_NOT_FOUND)
            with open(file, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/octet-stream',
                                        status=status.HTTP_200_OK)
                response['Content-Disposition'] = f'attachment; filename="{current_file.file_name}"'
            return response
        except Exception as e:
            logger.error(f"Error viewing file: {e}")
            return Response({"message": "Failed to view file"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def view_folder(request, folder_serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            current_folder = ShareFolder.objects.get(folder_serial=folder_serial,
                                                     user=auth['user']).first()
            if not current_folder:
                return Response({"message": "Folder not found"},
                                status=status.HTTP_404_NOT_FOUND)
            current_files = ShareFile.objects.filter(folder_serial=current_folder,
                                                     user=auth['user']).values('file_serial','file_name',
                                                                               'file_type','file_description')
            return Response({"message": "Folder details fetched successfully",
                             "data": current_files},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error viewing folder: {e}")
            return Response({"message": "Failed to view folder"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)