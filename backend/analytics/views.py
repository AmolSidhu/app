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

from .models import (
    DataSourceUpload, Dashboards, DashboardItem, DashboardTableDataLines,
    DashboardTableDataLines, DashboardGraphData, DashboardTextData)
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
            with open('json/directory.json', 'r') as f:
                directory = json.load(f)
            data_source_upload_dir = directory['data_source_raw_dir']
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
                raw_file_location=data_source_upload_dir,
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

@api_view(['PATCH'])
def update_data_source(request, serial):
    if request.method == 'PATCH':
        print('Updating data source')
        try:
            token = request.header.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            data_source = DataSourceUpload.objects.filter(serial=serial).first()
            if not data_source:
                return Response({'message': 'Data source not found'},
                                status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f'Error updating file: {e}')
            return Response({'message': 'Error uploading file'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['PATCH'])
def update_data_source_lines(request, serial):
    if request.method == 'PATCH':
        print('Updating data source lines')
        print(request.data.get('data'))
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            data_source = DataSourceUpload.objects.filter(serial=serial).first()
            if not data_source:
                return Response({'message': 'Data source not found'},
                                status=status.HTTP_404_NOT_FOUND)
            path = None
            if data_source.edited_file_location is None:
                with open('json/directory.json', 'r') as f:
                    directory = json.load(f)
                data_source.edited_file_location = directory['data_source_cleaned_dir']
                os.makedirs(data_source.edited_file_location, exist_ok=True)
                data_source.save()
            else:
                path = data_source.edited_file_location + data_source.serial + '.csv'
            print(f'Path: {path}')
            data = pd.DataFrame(request.data.get('data'))
            if data.empty:
                return Response({'message': 'No data to update'},
                                status=status.HTTP_202_ACCEPTED)
            df = pd.DataFrame(data)
            df.to_csv(path, index=False)
            column_names = {
                str(i + 1): [col, str(dtype)]
                for i, (col, dtype) in enumerate(zip(data.columns, data.dtypes))
            }
            data_source.column_names = column_names
            data_source.total_rows = df.shape[0]
            data_source.total_columns = df.shape[1]
            data_source.save()
            return Response({'message': 'Update Data Source Lines'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error updating data source lines: {e}')
            return Response({'message': 'Error updating data source lines'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def reset_data_source_lines(request, serial):
    if request.method == 'DELETE':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            data_source = DataSourceUpload.objects.filter(serial=serial,
                                                          user=auth_response['user']).first()
            if not data_source:
                return Response({'message': 'Data source not found'},
                                status=status.HTTP_404_NOT_FOUND)
            data_source_location = data_source.edited_file_location + serial + '.csv'
            if os.path.exists(data_source_location):
                os.remove(data_source_location)
            return Response({'message': 'Reset Data Source Lines'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error in authentication: {e}')
            return Response({'message': 'Authentication error'},
                            status=status.HTTP_403_FORBIDDEN)
            
@api_view(['GET'])
def get_data_source_cleaning_methods(request, serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            with open('json/options.json', 'r') as f:
                options = json.load(f)
            column_options = options['cleaning_methods_columns']
            row_options = options['cleaning_methods_rows']
            data_source = DataSourceUpload.objects.filter(serial=serial,
                                                          user=auth_response['user']).first()
            if data_source:
                print('Data source found')
                selected_column_options = None
                selected_row_options = None
                selected_override = data_source.override_column_cleaning
                if data_source.data_cleaning_method_for_columns != {}:
                    selected_column_options = data_source.data_cleaning_method_for_columns
                else:
                    selected_column_options = None
                if data_source.data_cleaning_method_for_rows != 'none':
                    selected_row_options = data_source.data_cleaning_method_for_rows
                else:
                    selected_row_options = None
            if not data_source:
                return Response({'message': 'Data source not found'},
                                status=status.HTTP_404_NOT_FOUND)
            return Response({'message': 'Get Data Source Cleaning Methods',
                             'columns': column_options,
                             'rows': row_options,
                             'selected_columns': selected_column_options,
                             'selected_rows': selected_row_options,
                             'selected_override': selected_override},
                             status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error getting data source cleaning methods: {e}')
            return Response({'message': 'Error getting data source cleaning methods'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['PATCH'])
def update_data_source_cleaning_methods(request, serial):
    if request.method == 'PATCH':
        print('Updating data source cleaning methods')
        print(request.data)
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            data_source = DataSourceUpload.objects.filter(serial=serial, user=auth_response['user']).first()
            if not data_source:
                return Response({'message': 'Data source not found'},
                                status=status.HTTP_404_NOT_FOUND)
            columns = (request.data.get('column_cleaning_methods'))
            rows = (request.data.get('row_cleaning_method'))
            override_columns = (request.data.get('override_column_with_row'))
            data_source.data_cleaning_method_for_columns = columns
            data_source.data_cleaning_method_for_rows = rows
            data_source.override_column_cleaning = override_columns
            data_source.data_cleaning_status = 'pending'
            data_source.save()
            return Response({'message': 'Update Data Source Cleaning Methods'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error updating data source cleaning methods: {e}')
            return Response({'message': 'Error updating data source cleaning methods'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_data_source_lines(request, serial):
    if request.method == 'GET':
        try:
            print('getting lines')
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            data_source = DataSourceUpload.objects.filter(serial=serial).first()
            if not data_source:
                print('no soruce found')
                return Response({'message': 'Data source not found'},
                                status=status.HTTP_404_NOT_FOUND)
            edited_path = data_source.edited_file_location
            raw_path = data_source.raw_file_location
            file_source = None
            print(f'{raw_path}/{serial}.csv')
            if edited_path and os.path.exists(edited_path + serial + '.csv'):
                file_source = edited_path + serial + '.csv'
            elif raw_path and os.path.exists(raw_path + serial + '.csv'):
                file_source = raw_path + serial + '.csv'
            else:
                (print('no file found'))
                return Response({'message': 'Data source file not found'},
                                status=status.HTTP_404_NOT_FOUND)
            with open(file_source, 'r') as file:
                data = pd.read_csv(file)
            data_json = data.to_dict(orient='records')
            data_row = data_source.column_names
            columns_cleaning_methods = data_source.data_cleaning_method_for_columns
            if not columns_cleaning_methods:
                columns_cleaning_methods = 'No cleaning method applied'
            rows_cleaning_method = data_source.data_cleaning_method_for_rows
            if rows_cleaning_method == 'none':
                rows_cleaning_method = 'No cleaning method applied'
            override_column_cleaning = data_source.override_column_cleaning
            if override_column_cleaning:
                override_column_cleaning = False
            return Response({'data': data_json,
                             'rows': data_row,
                             'columns_cleaning_methods': columns_cleaning_methods,
                             'rows_cleaning_method': rows_cleaning_method,
                             'override_column_cleaning': override_column_cleaning,
                             'message': 'Get Data Source Data'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error getting data source data: {e}')
            return Response({'message': 'Error getting data source data'},
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
            with open('directory.json', 'r') as f:
                directory = json.load(f)
            data_item_graph_dir = directory['data_item_graph_dir']
            os.makedirs(data_item_graph_dir, exist_ok=True)
            data_item_table_dir = directory['data_item_table_dir']
            os.makedirs(data_item_table_dir, exist_ok=True)
            data_item_truncate_dir = directory['data_item_truncate_dir']
            os.makedirs(data_item_truncate_dir, exist_ok=True)
            current_dashboard_item.graph_location = data_item_graph_dir
            current_dashboard_item.table_location = data_item_table_dir
            current_dashboard_item.table_truncated_location = data_item_truncate_dir
            current_dashboard_item.data_item_name = request.data['data_item_name'] 
            current_dashboard_item.data_item_description = request.data.get('data_item_description', '')
            current_dashboard_item.data_item_type = request.data['data_item_type']
            current_dashboard_item.data_item_created = False
            current_dashboard_item.data_item_failed_creation = False
            current_dashboard_item.save()
            if request.data['data_item_type'] == 'Graph':
                serial = None
                while serial is None:
                    serial = token_urlsafe(8)
                    if DashboardGraphData.objects.filter(serial=serial).exists():
                        serial = None
                new_graph_data = DashboardGraphData(
                        graph_type=request.data['graph_type'],
                        user=auth_response['user'],
                        dashboard_serial=current_dashboard,
                        dashboard_item_serial=current_dashboard_item,
                        serial=serial,
                        cleaning_method=request.data['cleaning_method'],
                        columns=request.data['columns'],
                        x_column=request.data['column_1'],
                        y_column=request.data['column_2'],
                        graph_title=request.data['graph_title'],
                        x_axis_title=request.data['x_axis_title'],
                        y_axis_title=request.data['y_axis_title'],       
                )
                new_graph_data.save()
            elif request.data['data_item_type'] == 'Table':
                for data_line in request.data['data_lines']:
                    serial = None
                    while serial is None:
                        serial = token_urlsafe(8)
                        if DashboardTableDataLines.objects.filter(serial=serial).exists():
                            serial = None
                    new_table_data_line = DashboardTableDataLines(
                        user=auth_response['user'],
                        dashboard_serial=current_dashboard,
                        dashboard_item_serial=current_dashboard_item,
                        serial=serial,
                        column_order=data_line['column_order'],
                        column_name=data_line['column_name'],
                        source_1=data_line.get('source_1', ''),
                        source_2=data_line['source_2'] if data_line['source_2'] else 'empty_source_2',
                        operation=data_line['operation'] if data_line['operation'] else 'empty_operation'
                    )
                    new_table_data_line.save()
            elif request.data['data_item_type'] == 'Text':
                serial = None
                while serial is None:
                    serial = token_urlsafe(8)
                    if DashboardTextData.objects.filter(serial=serial).exists():
                        serial = None
                new_text_data = DashboardTextData(
                    user=auth_response['user'],
                    dashboard_item_serial=current_dashboard_item,
                    dashboard_serial=current_dashboard,
                    serial=serial,
                    text_header=request.data.get('text_header', ''),
                    text_content=request.data['text_body']
                )
                new_text_data.save()
            else:
                return Response({'message': 'Invalid data item type'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({'message': 'Dashboard Item Data Created'},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f'Error creating dashboard item data: {e}')
            return Response({'message': 'Error creating dashboard item data'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['GET'])
def get_dashboard_item_serials(request, dashboard_serial):
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
            dashboard_items = DashboardItem.objects.filter(
                dashboard=current_dashboard,
                user=user
            ).values('dashboard_item_serial', 'item_type', 'item_order',
                     'data_item_name', 'data_item_description')
            if not dashboard_items:
                return Response({'message': 'No dashboard items found'},
                                status=status.HTTP_404_NOT_FOUND)
            dashboard_item_data = {}
            for item in dashboard_items:
                dashboard_item_data[item['dashboard_item_serial']] = {
                    'item_type': item['item_type'],
                    'item_order': item['item_order'],
                    'data_item_name': item['data_item_name'],
                    'data_item_description': item['data_item_description']
                }
            print(f'Dashboard Item Data: {dashboard_item_data}')
            return Response({'dashboard_items': dashboard_item_data,
                             'message': 'Get Dashboard Item Serial Numbers'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error fetching dashboard item serials: {e}')
            return Response({'message': 'Error fetching dashboard item serials'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_dashboard_item(request, dashboard_serial, dashboard_item_serial):
    if request.method == 'GET':
        print('Getting dashboard item')
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
            data_source = current_dashboard.data_source
            if not data_source:
                return Response({'message': 'Data source not found'},
                                status=status.HTTP_404_NOT_FOUND)
            data = {}
            data['item_type'] = current_dashboard_item.item_type
            data['item_order'] = current_dashboard_item.item_order
            data['data_item_name'] = current_dashboard_item.data_item_name
            data['data_item_description'] = current_dashboard_item.data_item_description
            if current_dashboard_item.item_type == 'Graph':
                current_graph_settings = DashboardGraphData.objects.filter(
                    dashboard_item_serial=current_dashboard_item,
                    user=user
                ).first()
                if not current_graph_settings:
                    return Response({'message': 'Graph settings not found'},
                                    status=status.HTTP_404_NOT_FOUND)
                with open('options.json', 'r') as f:
                    options = json.load(f)
                
                data['graph_type'] = options['graph_types']
                data['column_1'] = current_graph_settings.x_column
                data['column_2'] = current_graph_settings.y_column
                data['current_graph_type'] = current_graph_settings.graph_type
                data['graph_title'] = current_graph_settings.graph_title
                data['x_axis_title'] = current_graph_settings.x_axis_title
                data['y_axis_title'] = current_graph_settings.y_axis_title
            if current_dashboard_item.item_type == 'Table':
                dashboard_item_table_lines = DashboardTableDataLines.objects.filter(
                    dashboard_item_serial=current_dashboard_item,
                    dashboard_serial=current_dashboard,
                    user=user
                ).values(
                    'serial', 'column_order', 'column_name', 'source_1', 'source_2', 'operation'
                )
                data['data_lines'] = list(dashboard_item_table_lines)
            if current_dashboard_item.item_type == 'Text':
                current_text_item = DashboardTextData.objects.filter(
                    dashboard_item_serial=current_dashboard_item,
                    user=user
                ).first()
                if not current_text_item:
                    return Response({'message': 'Dashboard item text not found'},
                                    status=status.HTTP_404_NOT_FOUND)
                data['text_header'] = current_text_item.text_header
                data['text_body'] = current_text_item.text_content
            return Response({'data': data,
                             'message': 'Get Dashboard Item'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error getting dashboard item: {dashboard_item_serial} for dashboard: {dashboard_serial} - {e}')
            return Response({'message': 'Error getting dashboard item'},
                            status=status.HTTP_403_FORBIDDEN)
            
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
            current_dashboard_item.data_item_name = request.data['data_item_name']
            current_dashboard_item.data_item_type = request.data['item_type']
            current_dashboard_item.data_item_description = request.data.get('data_item_description', '')
            current_dashboard_item.data_item_created = False
            current_dashboard_item.data_item_failed_creation = False
            current_dashboard_item.save()
            item_types = ['Graph', 'Table', 'Text']
            if request.data.get('data_item_type') not in item_types:
                return Response({'message': 'Data Item Type does not match any existing item type'},
                                status=status.HTTP_405_METHOD_NOT_ALLOWED)
            if request.data.get('data_item_type') == 'Graph':
                current_graph_settings = DashboardGraphData.objects.filter(
                    dashboard_item_serial=current_dashboard_item,
                    user=auth_response['user']
                ).first()
                if not current_graph_settings:
                    return Response({'message': 'Graph settings not found'},
                                    status=status.HTTP_404_NOT_FOUND)
                current_graph_settings.graph_type = request.data['graph_type']
                current_graph_settings.columns = request.data['columns']
                current_graph_settings.x_column = request.data['column_1']
                current_graph_settings.y_column = request.data['column_2']
                current_graph_settings.graph_title = request.data['graph_title']
                current_graph_settings.x_axis_title = request.data['x_axis_title']
                current_graph_settings.y_axis_title = request.data['y_axis_title']
                current_graph_settings.save()
            if request.data.get('data_item_type') == 'Table':
                dashboard_item_table_lines = DashboardTableDataLines.objects.filter(
                    dashboard_item_serial=current_dashboard_item,
                    dashboard_serial=current_dashboard,
                    user=auth_response['user']
                )
                dashboard_item_table_lines.delete()
                for data_line in request.data['data_lines']:
                    serial = None
                    while serial is None:
                        serial = token_urlsafe(8)
                        if DashboardTableDataLines.objects.filter(serial=serial).exists():
                            serial = None
                    new_table_data_line = DashboardTableDataLines(
                        user=auth_response['user'],
                        dashboard_serial=current_dashboard,
                        dashboard_item_serial=current_dashboard_item,
                        serial=serial,
                        column_order=data_line['column_order'],
                        column_name=data_line['column_name'],
                        source_1=data_line.get('source_1', ''),
                        source_2=data_line['source_2'] if data_line['source_2'] else 'empty_source_2',
                        operation=data_line['operation'] if data_line['operation'] else 'empty_operation'
                    )
                    new_table_data_line.save()
            if request.data.get('data_item_type') == 'Text':
                current_text_item = DashboardTextData.objects.filter(
                    dashboard_item_serial=current_dashboard_item,
                    user=auth_response['user']
                ).first()
                if not current_text_item:
                    return Response({'message': 'Dashboard item text not found'},
                                    status=status.HTTP_404_NOT_FOUND)
                current_text_item.text_header = request.data.get('text_header', '')
                current_text_item.text_content = request.data['text_content']
                current_text_item.save()
            else:
                return Response({'message': 'Invalid data item type'},
                                status=status.HTTP_400_BAD_REQUEST)
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

@api_view(['DELETE'])
def delete_dashboard(request, serial):
    if request.method == 'DELETE':
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
            current_dashboard.delete()
            return Response({'message': 'Delete Dashboard'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error deleting dashboard: {e}')
            return Response({'message': 'Error deleting dashboard'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
         
@api_view(['GET'])
def get_data_sources(request):
    if request.method == 'GET':
        print('Getting data sources')
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
                print(data)
                return Response({'data': data},
                                status=status.HTTP_200_OK)
            return Response({'message': 'No data sources found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f'Error getting data sources: {e}')
            return Response({'message': 'Error getting data sources'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_cleaned_data_sources(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({'message': f'{auth_response["error"]}'},
                                status=status.HTTP_403_FORBIDDEN)
            data_sources = DataSourceUpload.objects.filter(
                user=auth_response['user'],
                data_cleaning_status='cleaned'
            ).values(
                'serial', 'data_source_name', 'file_name'
            )
            data = list(data_sources)
            if len(data) > 0:
                return Response({'data': data},
                                status=status.HTTP_200_OK)
            return Response({'message': 'No cleaned data sources found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f'Error getting cleaned data sources: {e}')
            return Response({'message': 'Error getting cleaned data sources'},
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
                            status=status.HTTP_200_OK)
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
        except Exception as e:
            logger.error(f'Error in authentication: {e}')
            return Response({'message': 'Authentication error'},
                            status=status.HTTP_403_FORBIDDEN)

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

