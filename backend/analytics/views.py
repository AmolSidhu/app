from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from secrets import token_urlsafe

import os
import json
import logging
import pandas as pd

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
            with open('directory.json', 'r') as f:
                directory = json.load(f)
            data_source_upload_dir = directory['data_source_upload_dir']
            os.makedirs(data_source_upload_dir, exist_ok=True)

            file = request.FILES['file']
            if file.name.split('.')[-1] != 'csv':
                return Response({'message': 'Invalid file type. Please upload a CSV file'},
                                status=status.HTTP_400_BAD_REQUEST)
            unique_token = False
            while not unique_token:
                serial = token_urlsafe(8)
                if not DataSourceUpload.objects.filter(serial=serial).exists():
                    unique_token = True
            data = pd.read_csv(file)
            column_names = {
                str(i + 1): [col, str(dtype)]
                for i, (col, dtype) in enumerate(zip(data.columns, data.dtypes))
            }
            total_rows = data.shape[0]
            total_columns = data.shape[1]
            file_location = os.path.join(data_source_upload_dir, f'{serial}.csv')
            data.to_csv(file_location, index=False)
            DataSourceUpload.objects.create(
                user=user,
                serial=serial,
                file_location=data_source_upload_dir,
                file_name=file.name.split('.')[0],
                column_names=column_names,
                data_source_name=request.data['data_source_name'],
                total_rows=total_rows,
                total_columns=total_columns,
                date_uploaded=timezone.now()
            )
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
            
@api_view(['GET'])
def get_data_sources(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            data_sources = DataSourceUpload.objects.filter(user=auth_response['user']).values(
                'serial', 'data_source_name', 'file_name'
            )
            data = list(data_sources)
            if len(data) > 0:
                return Response({'data': data},
                                status=status.HTTP_200_OK)
            return Response({'message': 'No data sources found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f'Error getting data sources: {e}')
            return Response({'message': 'Error getting data sources'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_data_source_details(request, serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            data_source = DataSourceUpload.objects.filter(user=user, serial=serial).first()
            if not data_source:
                return Response({'message': 'Data source not found'},
                                status=status.HTTP_404_NOT_FOUND)
            return Response({'data': data_source,
                             'message': 'Get Data Source Details'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error getting data source details: {e}')
            return Response({'message': 'Error getting data source details'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def create_dashboard_item(request, serial):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            if request.data['data_item_type'] == 'chart':
                return Response({'message': 'Create Chart Item'},
                            status=status.HTTP_201_CREATED)
            elif request.data['data_item_type'] == 'table':
                return Response({'message': 'Create Table Item'},
                            status=status.HTTP_201_CREATED)
            elif request.data['data_item_type'] == 'text':
                return Response({'message': 'Create Text Item'},
                            status=status.HTTP_201_CREATED)
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
def get_dashboard_item(request, serial):
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