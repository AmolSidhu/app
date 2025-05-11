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

from .models import DataSourceUpload, Dashboards, DashboardItem, DashboardItemData

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
            serial = None
            while serial is None:
                serial = token_urlsafe(8)
                if Dashboards.objects.filter(dashboard_serial=serial).exists():
                    serial = None
            new_dashboard = Dashboards(
                user=auth_response['user'],
                data_source=DataSourceUpload.objects.get(serial=request.data['data_source_serial']),
                dashboard_serial=serial,
                dashboard_name=request.data['dashboard_name'],
                dashboard_data_order={},
                date_created=timezone.now(),
                date_last_updated=timezone.now()
            )
            new_dashboard.save()
            return Response({'message': 'Create Dashboard'},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f'Error creating dashboard: {e}')
            return Response({'message': 'Error creating dashboard'},
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
            current_dashboard = Dashboards.objects.filter(dashboard_serial=serial).first()
            if not current_dashboard:
                return Response({'message': 'Dashboard not found'},
                                status=status.HTTP_404_NOT_FOUND)
            serial = None
            while serial is None:
                serial = token_urlsafe(8)
                if DashboardItem.objects.filter(dashboard_item_serial=serial).exists():
                    serial = None
            new_dashboard_item = DashboardItem(
                user=auth_response['user'],
                dashboard=current_dashboard,
                dashboard_item_serial=serial,
                dashboard_data_serial=current_dashboard.data_source,
                item_type=request.data['item_type'],
                item_order=request.data['item_order'],
            )
            new_dashboard_item.save()
            return Response({'message': 'Create Dashboard Item'},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f'Error creating dashboard item: {e}')
            return Response({'message': 'Error creating dashboard item'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def create_dashboard_item_data(request, dashboard_serial, dashboard_item_serial):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            current_dashboard = Dashboards.objects.filter(
                dashboard_serial=dashboard_serial,
                user=auth_response['user']
            ).first()
            if not current_dashboard:
                return Response({'message': 'Dashboard not found'},
                                status=status.HTTP_404_NOT_FOUND)
            current_dashboard_item = DashboardItem.objects.filter(
                dashboard_item_serial=dashboard_item_serial,
                dashboard=current_dashboard,
                user=auth_response['user']
            ).first()
            if not current_dashboard_item:
                return Response({'message': 'Dashboard item not found'},
                                status=status.HTTP_404_NOT_FOUND)
            item_types = ['Graph', 'Table', 'Text']
            if request.data.get('data_item_type') not in item_types:
                return Response({'message': 'Data Item Type does not match any existing item type'},
                                status=status.HTTP_405_METHOD_NOT_ALLOWED)
            serial = None
            while serial is None:
                serial = token_urlsafe(8)
                if DashboardItemData.objects.filter(serial=serial).exists():
                    serial = None
            with open('directory.json', 'r') as f:
                directory = json.load(f)
            data_source_item_dir = directory['data_source_item_dir']
            os.makedirs(data_source_item_dir, exist_ok=True)
            new_dashboard_item_data = DashboardItemData(
                user=auth_response['user'],
                serial=serial,
                dashboard_item=current_dashboard_item,
                dashboard_item_location=data_source_item_dir,
                data_item_name=request.data['data_item_name'],
                data_item_type=request.data['data_item_type'],
            )
            new_dashboard_item_data.save()
            if request.data.get('data_item_type') == 'Graph':
                pass
            elif request.data.get('data_item_type') == 'Table':
                pass
            elif request.data.get('data_item_type') == 'Text':
                pass
            else:
                return Response({'message': 'Invalid data item type'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({'message': 'Create Dashboard Item Data'},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f'Error creating dashboard item data: {e}')
            return Response({'message': 'Error creating dashboard item data'},
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