from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from secrets import token_urlsafe
from django.db import connection

import os
import json
import logging
import pandas as pd

from functions.auth_functions import auth_check

from .models import DataSourceUpload, Dashboards, DashboardItem, DashboardItemData
from .models import DashboardItemTable, DashboardItemGraph, DashboardItemText, DashboardItemTableLines, GraphSettings
from .queries import get_all_dashbaord_items

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
            return Response({'dashboard_item_serial': serial,
                            'message': 'Create Dashboard Item'},
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
                data_item_location=data_source_item_dir,
                data_item_name=request.data['data_item_name'],
                data_item_type=request.data['data_item_type'],
            )
            new_dashboard_item_data.save()
            if request.data.get('data_item_type') == 'Graph':
                graph_type = ['pie', 'bar', 'line', 'scatter', 'heatmap', 'box', 'violin']
                if request.data['graph_type'] not in graph_type:
                    return Response({'message': 'Graph type does not match any existing graph type'},
                                    status=status.HTTP_405_METHOD_NOT_ALLOWED)
                cleaning_method = ['drop_duplicates', 'drop_columns', 'drop_rows', 'replace', 'fillna']
                if request.data['cleaning_method'] not in cleaning_method:
                    return Response({'message': 'Cleaning method does not match any existing cleaning method'},
                                    status=status.HTTP_405_METHOD_NOT_ALLOWED)
                serial = None
                while serial is None:
                    serial = token_urlsafe(8)
                    if DashboardItemGraph.objects.filter(serial=serial).exists():
                        serial = None
                    new_graph_item = DashboardItemGraph(
                        user=auth_response['user'],
                        serial=serial,
                        dashboard_item_serial=current_dashboard_item,
                        dashboard_item_data_serial=new_dashboard_item_data,
                        dashboard_serial=current_dashboard,
                    )
                    new_graph_item.save()
                    serial = None
                    while serial is None:
                        serial = token_urlsafe(8)
                        if GraphSettings.objects.filter(graph_settings_serial=serial).exists():
                            serial = None
                    new_graph_settings = GraphSettings(
                        graph_type=request.data['graph_type'],
                        user=auth_response['user'],
                        dashboard =current_dashboard,
                        dashboard_item=current_dashboard_item,
                        dashboard_item_graph=new_graph_item,
                        graph_settings_serial=serial,
                        cleaning_method=request.data['cleaning_method'],
                        columns=request.data['columns'],
                        x_column=request.data['column_1'],
                        y_column=request.data['column_2'],
                        graph_title=request.data['graph_title'],
                        x_axis_title=request.data['x_axis_title'],
                        y_axis_title=request.data['y_axis_title'],
                    )
                    new_graph_settings.save()
            elif request.data.get('data_item_type') == 'Table':
                serial = None
                while serial is None:
                    serial = token_urlsafe(8)
                    if DashboardItemTable.objects.filter(serial=serial).exists():
                        serial = None
                    new_table_item = DashboardItemTable(
                        user=auth_response['user'],
                        serial=serial,
                        dashboard_item_serial=current_dashboard_item,
                        dashboard_item_data_serial=new_dashboard_item_data,
                        dashboard_serial=current_dashboard,
                    )
                    new_table_item.save()
                    for data_line in request.data['data_lines']:
                        serial = None
                        while serial is None:
                            serial = token_urlsafe(8)
                            if DashboardItemTableLines.objects.filter(serial=serial).exists():
                                serial = None
                        new_table_line = DashboardItemTableLines(
                            user=auth_response['user'],
                            serial=serial,
                            dashboard_item_table_serial=new_table_item,
                            dashboard_table_serial=current_dashboard_item,
                            dashboard_serial=current_dashboard,
                            column_order=data_line['column_order'],
                            column_name=data_line['column_name'],
                            source_1=data_line['source_1'],
                            source_2=data_line['source_2'] if data_line['source_2'] else 'empty_source_2',
                            operation=data_line['operation'] if data_line['operation'] else 'empty_operation',
                        )
                        new_table_line.save()
            elif request.data.get('data_item_type') == 'Text':
                serial = None
                while serial is None:
                    serial = token_urlsafe(8)
                    if DashboardItemText.objects.filter(serial=serial).exists():
                        serial = None
                    new_text_item = DashboardItemText(
                        user=auth_response['user'],
                        serial=serial,
                        dashboard_item_serial=current_dashboard_item,
                        dashboard_item_data_serial=new_dashboard_item_data,
                        dashboard_serial=current_dashboard,
                        text_header=request.data['text_header'],
                        text_body=request.data['text_body'],
                    )
                    new_text_item.save()
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
def get_dashboard_item(request, dashboard_serial, dashboard_item_serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            current_dashboard = Dashboards.objects.filter(
                dashboard_serial=dashboard_serial,
                user=user
            ).first()  
            if not current_dashboard:
                return Response({'message': 'Dashboard not found'},
                                status=status.HTTP_404_NOT_FOUND)
            current_dashboard_item = DashboardItem.objects.filter(
                dashboard_item_serial=dashboard_item_serial,
                dashboard=current_dashboard,
                user=user
            ).first()
            if current_dashboard_item is None:
                return Response({'message': 'Dashboard item not found'},
                                status=status.HTTP_404_NOT_FOUND)
            data = {}
            data['item_type'] = current_dashboard_item.item_type
            data['item_order'] = current_dashboard_item.item_order
            if current_dashboard_item.item_type == 'Graph':
                current_graph_settings = GraphSettings.objects.filter(
                    dashboard_item=current_dashboard_item,
                    user=user
                ).first()
                if not current_graph_settings:
                    return Response({'message': 'Graph settings not found'},
                                    status=status.HTTP_404_NOT_FOUND)
                data['graph_type'] = current_graph_settings.graph_type
                data['cleaning_method'] = current_graph_settings.cleaning_method
                data['columns'] = current_graph_settings.columns
                data['column_1'] = current_graph_settings.x_column
                data['column_2'] = current_graph_settings.y_column
                data['graph_title'] = current_graph_settings.graph_title
                data['x_axis_title'] = current_graph_settings.x_axis_title
                data['y_axis_title'] = current_graph_settings.y_axis_title
            if current_dashboard_item.item_type == 'Table':
                current_table_item = DashboardItemTable.objects.filter(
                    dashboard_item_serial=current_dashboard_item,
                    user=user
                ).first()
                if not current_table_item:
                    return Response({'message': 'Dashboard item table not found'},
                                    status=status.HTTP_404_NOT_FOUND)
                dashboard_item_table_lines = DashboardItemTableLines.objects.filter(
                    dashboard_item_table_serial=current_table_item,
                    user=user
                ).values(
                    'serial', 'column_order', 'column_name', 'source_1', 'source_2', 'operation'
                )
                data['data_lines'] = list(dashboard_item_table_lines)
            if current_dashboard_item.item_type == 'Text':
                current_text_item = DashboardItemText.objects.filter(
                    dashboard_item_serial=current_dashboard_item,
                    user=user
                ).first()
                if not current_text_item:
                    return Response({'message': 'Dashboard item text not found'},
                                    status=status.HTTP_404_NOT_FOUND)
                data['text_header'] = current_text_item.text_header
                data['text_body'] = current_text_item.text_body
            return Response({'data': data,
                             'message': 'Get Dashboard Item'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error getting dashboard item: {e}')
            return Response({'message': 'Error getting dashboard item'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def update_dashboard_item(request, dashboard_serial, dashboard_item_serial):
    if request.method == 'PATCH':
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
            current_dashboard_item = DashboardItem(
                item_type=request.data['item_type'],
                item_order=request.data['item_order'],
            )
            current_dashboard_item.save()
            current_dashboard_item_data = DashboardItemData.objects.filter(
                dashboard_item=current_dashboard_item,
                user=auth_response['user']
            ).first()
            if not current_dashboard_item_data:
                return Response({'message': 'Dashboard item data not found'},
                                status=status.HTTP_404_NOT_FOUND)
            current_dashboard_item_data.data_item_name = request.data['data_item_name']
            current_dashboard_item_data.data_item_type = request.data['item_type']
            current_dashboard_item_data.data_item_description = request.data.get('data_item_description', '')
            current_dashboard_item_data.save()
            item_types = ['Graph', 'Table', 'Text']
            if request.data.get('data_item_type') not in item_types:
                return Response({'message': 'Data Item Type does not match any existing item type'},
                                status=status.HTTP_405_METHOD_NOT_ALLOWED)
            if request.data.get('data_item_type') == 'Graph':
                graph_type = ['pie', 'bar', 'line', 'scatter', 'heatmap', 'box', 'violin']
                if request.data['graph_type'] not in graph_type:
                    return Response({'message': 'Graph type does not match any existing graph type'},
                                    status=status.HTTP_405_METHOD_NOT_ALLOWED)
                cleaning_method = ['drop_duplicates', 'drop_columns', 'drop_rows', 'replace', 'fillna']
                if request.data['cleaning_method'] not in cleaning_method:
                    return Response({'message': 'Cleaning method does not match any existing cleaning method'},
                                    status=status.HTTP_405_METHOD_NOT_ALLOWED)
                current_graph_item = DashboardItemGraph.objects.filter(
                    dashboard_item_serial=current_dashboard_item,
                    user=auth_response['user']
                ).first()
                if not current_graph_item:
                    return Response({'message': 'Dashboard item graph not found'},
                                    status=status.HTTP_404_NOT_FOUND)
                current_graph_item.graph_created = False
                current_graph_item.graph_failed = False
                current_graph_item.save()
                current_grpah_settings = GraphSettings.objects.filter(
                    dashboard_item_graph=current_graph_item,
                    user=auth_response['user']
                ).first()    
                if not current_grpah_settings:
                    return Response({'message': 'Graph settings not found'},
                                    status=status.HTTP_404_NOT_FOUND)
                current_grpah_settings.graph_type = request.data['graph_type']
                current_grpah_settings.cleaning_method = request.data['cleaning_method']
                current_grpah_settings.columns = request.data['columns']
                current_grpah_settings.x_column = request.data['column_1']
                current_grpah_settings.y_column = request.data['column_2']
                current_grpah_settings.graph_title = request.data['graph_title']
                current_grpah_settings.x_axis_title = request.data['x_axis_title']
                current_grpah_settings.y_axis_title = request.data['y_axis_title']
                current_grpah_settings.save()
            if request.data.get('data_item_type') == 'Table':
                current_table_item = DashboardItemTable.objects.filter(
                    dashboard_item_serial=current_dashboard_item,
                    user=auth_response['user']
                ).first()
                current_table_item.table_created = False
                current_table_item.table_failed = False
                current_table_item.save()
                if not current_table_item:
                    return Response({'message': 'Dashboard item table not found'},
                                    status=status.HTTP_404_NOT_FOUND)
                for data_line in request.data['data_lines']:
                    current_table_line = DashboardItemTableLines.objects.filter(
                        dashboard_item_table_serial=current_table_item,
                        user=auth_response['user'],
                        serial =data_line['serial']
                    ).first()
                    if not current_table_line:
                        return Response({'message': 'Dashboard item table line not found'},
                                        status=status.HTTP_404_NOT_FOUND)
                    current_table_line.column_order = data_line['column_order']
                    current_table_line.column_name = data_line['column_name']
                    current_table_line.source_1 = data_line['source_1']
                    current_table_line.source_2 = data_line['source_2'] if data_line['source_2'] else 'empty_source_2'
                    current_table_line.operation = data_line['operation'] if data_line['operation'] else 'empty_operation'
                    current_table_line.save()
            if request.data.get('data_item_type') == 'Text':
                current_text_item = DashboardItemText.objects.filter(
                    dashboard_item_serial=current_dashboard_item,
                    user=auth_response['user']
                ).first()
                if not current_text_item:
                    return Response({'message': 'Dashboard item text not found'},
                                    status=status.HTTP_404_NOT_FOUND)
                current_text_item.text_header = request.data['text_header']
                current_text_item.text_body = request.data['text_body']
                current_text_item.save()     
            return Response({'message': 'Update Dashboard Item'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error updating dashboard item: {e}')
            return Response({'message': 'Error updating dashboard item'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def delete_dashboard_item(request, dashboard_serial, dashboard_item_serial):
    if request.method == 'DELETE':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            return Response({'message': 'Delete Dashboard Item'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error deleting dashboard item: {e}')
            return Response({'message': 'Error deleting dashboard item'},
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
    try:
        token = request.headers.get('Authorization')
        auth_response = auth_check(token)
        if 'error' in auth_response:
            return Response({'message': f'{auth_response["error"]}'},
                            status=status.HTTP_403_FORBIDDEN)
        user = auth_response['user']
        current_dashboard = Dashboards.objects.filter(
            dashboard_serial=serial,
            user=user
        ).first()
        if not current_dashboard:
            return Response({'message': 'Dashboard not found'},
                            status=status.HTTP_404_NOT_FOUND)
        data_source = current_dashboard.data_source
        if not data_source:
            return Response({'message': 'Data source not found'},
                            status=status.HTTP_404_NOT_FOUND)
        data = data_source.column_names
        return Response({'data': data,
                         'message': 'Get Data Source Details'},
                        status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f'Error getting data source details: {e}')
        return Response({'message': 'Error getting data source details'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_dashboards(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            dashboards = Dashboards.objects.filter(user=auth_response['user']).values(
                'dashboard_serial', 'dashboard_name', 'date_created'
            )
            data = list(dashboards)
            if len(data) > 0:
                return Response({'data': data},
                                status=status.HTTP_200_OK)
            return Response({'message': 'No dashboards found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f'Error getting dashboards: {e}')
            return Response({'message': 'Error getting dashboards'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_dashboard(request, serial):
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
def get_dashboard_items(request, serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            dashboard = Dashboards.objects.filter(
                dashboard_serial=serial,
                user=user
            ).first()
            if not dashboard:
                return Response({'message': 'Dashboard not found'},
                                status=status.HTTP_404_NOT_FOUND)
            dashboard_items = DashboardItem.objects.filter(
                dashboard=dashboard,
                user=user
            ).values(
                'dashboard_item_serial', 'item_type', 'item_order'
            )
            data = list(dashboard_items)
            return Response({'data': data,
                             'message': 'Get Dashboard Item'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error getting dashboard item: {e}')
            return Response({'message': 'Error getting dashboard item'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_dashboard_item_output(request, serial, item_order):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            dashboard_data_records = DashboardItemData.objects.filter(
                dashboard_data_serial=serial,
                user=user,
                data_order=item_order
            ).values(
                'serial', 'dashboard_item_serial', 'data_item_type', 'data_item_location'
            )
            
        except Exception as e:
            logger.error(f'Error getting dashboard item output: {e}')
            return Response({'message': 'Error getting dashboard item output'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def setup_report(request):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            return Response({'message': 'Setup Report'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error setting up report: {e}')
            return Response({'message': 'Error setting up report'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def create_report_settings(request, serial):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            return Response({'message': 'Create Report Settings'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error creating report settings: {e}')
            return Response({'message': 'Error creating report settings'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_report_settings(request, serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            return Response({'message': 'Get Report Settings'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error getting report settings: {e}')
            return Response({'message': 'Error getting report settings'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def update_report_settings(request, serial):
    if request.method == 'PATCH':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            return Response({'message': 'Update Report Settings'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error updating report settings: {e}')
            return Response({'message': 'Error updating report settings'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def delete_report_settings(request, serial):
    if request.method == 'DELETE':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            user = auth_response['user']
            return Response({'message': 'Delete Report Settings'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error deleting report settings: {e}')
            return Response({'message': 'Error deleting report settings'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

