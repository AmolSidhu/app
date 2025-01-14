from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from secrets import token_urlsafe

import logging

from functions.auth_functions import auth_check

from .models import DataSourceUpload

logger = logging.getLogger(__name__)

@api_view(['POST'])
def upload_data_source(request):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            file = request.FILES['file']
            if file.name.split('.')[-1] != 'csv':
                return Response({'message': 'Invalid file type. Please upload a CSV file'},
                                status=status.HTTP_400_BAD_REQUEST)
            unique_token = False
            while not unique_token:
                serial = token_urlsafe(8)
                if not DataSourceUpload.objects.filter(serial=serial).exists():
                    unique_token = True
            return Response({'message': 'Upload Data Source'},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f'Error uploading file: {e}')
            return Response({'message': 'Error uploading file'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['POST'])
def create_dashboard(request):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            return Response({'message': 'Create Dashboard'},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f'Error creating dashboard: {e}')
            return Response({'message': 'Error creating dashboard'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def create_dashboard_item(request):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            return Response({'message': 'Create Dashboard Item'},
                            status=status.HTTP_201_CREATED)     
        except Exception as e:
            logger.error(f'Error creating dashboard item: {e}')
            return Response({'message': 'Error creating dashboard item'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_dashboard(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            return Response({'message': 'Get Dashboard'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error getting dashboard: {e}')
            return Response({'message': 'Error getting dashboard'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_dashboard_item(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            return Response({'message': 'Get Dashboard Item'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error getting dashboard item: {e}')
            return Response({'message': 'Error getting dashboard item'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)