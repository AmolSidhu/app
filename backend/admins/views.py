from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status

import logging
import json
import os

from functions.auth_functions import auth_check, admin_auth_check, admin_token_generator
from functions.serial_default_generator import generate_serial_code

from user.models import AdminCredentials
from videos.models import VideoRequest

logger = logging.getLogger(__name__)

@api_view(['PATCH'])
def admin_login(request):
    if request.method == 'PATCH':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return auth_response['error']
            admin_user = AdminCredentials.objects.filter(
                admin_username=auth_response['user']).first()
            if admin_user is None:
                return Response({'message': 'Admin user not found'},
                                status=status.HTTP_404_NOT_FOUND)
            if admin_user.active_admin is False: 
                return Response({'message': 'Admin user is not active'},
                                status=status.HTTP_403_FORBIDDEN)
            if request.data.get('email') != admin_user.admin_email:
                return Response({'message': 'Invalid email'},
                                status=status.HTTP_400_BAD_REQUEST)
            generate_admin_token = admin_token_generator(
                username = admin_user.admin_username.username,
                email = admin_user.admin_email,
                admin_code = admin_user.admin_code
            )
            return Response({
                'message': 'Admin login successful',
                'admin_token': generate_admin_token
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Import Error in admin login: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            
@api_view(['GET'])
def video_request_options(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return auth_response['error']
            admin_token = request.headers.get('Admin-Token')
            admin_auth_response = admin_auth_check(admin_token)
            if 'error' in admin_auth_response:
                return admin_auth_response['error']
            with open('json/options.json') as options_file:
                options_data = json.load(options_file)
            return Response({
                'message': 'Video request options fetched successfully',
                'data': options_data['admin_video_review_status']
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in fetching video request options: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['GET'])
def video_requests(request, status_filter):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return auth_response['error']
            admin_token = request.headers.get('Admin-Token')
            admin_auth_response = admin_auth_check(admin_token)
            if 'error' in admin_auth_response:
                return admin_auth_response['error']
            with open('json/options.json') as options_file:
                options_data = json.load(options_file)
            if status_filter not in options_data['admin_video_review_status']:
                return Response({'message': 'Invalid status filter'},
                                status=status.HTTP_400_BAD_REQUEST)
            records_to_review = VideoRequest.objects.filter(request_status=status_filter
                                                            ).order_by('request_date')[:100]
            request_data = {}
            x = 1
            for request_record in records_to_review:
                request_data[x] = { 
                    'serial': request_record.serial,
                    'username': request_record.user.username,
                    'request_date': request_record.request_date,
                    'requeset_title': request_record.request_title,
                    'request_description': request_record.request_description,
                }
                x += 1
            return Response({
                'message': 'Video requests fetched successfully',
                'data': request_data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in video requests: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def review_video_request(request, serial):
    if request.method == 'PATCH':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return auth_response['error']
            admin_token = request.headers.get('Admin-Token')
            admin_auth_response = admin_auth_check(admin_token)
            if 'error' in admin_auth_response:
                return admin_auth_response['error']
            admin_user = admin_auth_response['user']
            video_request = VideoRequest.objects.filter(serial=serial).first()
            if video_request is None:
                return Response({'message': 'Video request not found'},
                                status=status.HTTP_404_NOT_FOUND)
            with open('json/options.json') as options_file:
                options_data = json.load(options_file)
            if request.data.get('request_status') not in options_data['admin_video_review_status']:
                return Response({'message': 'Invalid request status'},
                                status=status.HTTP_400_BAD_REQUEST)
            video_request.request_status = request.data.get('request_status')
            video_request.reviewed_by = admin_user
            video_request.save() 
            return Response({
                'message': 'Video request reviewed successfully'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in reviewing video request: {str(e)}")
            return Response({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)