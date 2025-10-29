from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import FileResponse
from django.utils import timezone
from rest_framework import status

import logging
import json
import os

from functions.auth_functions import auth_check
from functions.serial_default_generator import generate_serial_code

from .models import ScraperUploadFile, ScraperOutputFile

logger = logging.getLogger(__name__)

@api_view(['POST'])
def create_new_scraper(request):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({"error": "Unauthorized"},
                                status=status.HTTP_401_UNAUTHORIZED)
            file = request.FILES.get('file')
            if not file:
                return Response({"error": "No file provided"},
                                status=status.HTTP_400_BAD_REQUEST)
            if not file.name.endswith('.csv'):
                return Response({"error": "Invalid file type. Only CSV files are allowed."},
                                status=status.HTTP_400_BAD_REQUEST)
            with open('json/directory.json') as f:
                directory = json.load(f)
            upload_path = directory['mtg_upload_dir']
            os.makedirs(upload_path, exist_ok=True)
            serial = generate_serial_code(
                config_section='mtg',
                serial_key='mtg_csv_upload_serial_code',
                model=ScraperUploadFile,
                field_name='serial'
            )
            file_path = os.path.join(upload_path, f"{serial}.csv")
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            scraper_file = ScraperUploadFile.objects.create(
                user_id=auth_response['user'],
                file_name=file.name,
                serial=serial,
                file_location=upload_path,
                scraper_name=request.data.get('scraper_name', 'mtg_f2f_scraper'),
                file_type=file.name.split('.')[-1],
                create_date=timezone.now(),
                update_date=timezone.now()
            )
            scraper_file.save()
            return Response({
                "message": "File uploaded successfully",},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error in create_new_scraper: {e}")
            return Response({"error": "Internal server error"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_default_template(request):
    if request.method == 'GET':
        print("get_default_template called")
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({"error": "Unauthorized"},
                                status=status.HTTP_401_UNAUTHORIZED)
            base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            template_path = os.path.join(base, 'templates', 'mtg',
                                         'default_template.csv')
            if not os.path.exists(template_path):
                return Response({"error": f"Template file not found at {template_path}"},
                                status=status.HTTP_404_NOT_FOUND)
            file = open(template_path, 'rb')
            response = FileResponse(
                file,
                as_attachment=True,
                filename='default_template.csv',
                content_type='text/csv',
                status=status.HTTP_200_OK
            )
            return response
        except Exception as e:
            logger.error(f"Error in get_default_template: {e}")
            return Response({"error": "Internal server error"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['GET'])
def get_download_scraper_output(request, serial_scraper, serial_output):
    if request.method == 'GET':
        try:
            print(f'serial_scraper: {serial_scraper}, serial_output: {serial_output}')
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({"error": "Unauthorized"},
                                status=status.HTTP_401_UNAUTHORIZED)
            scraper = ScraperUploadFile.objects.filter(serial=serial_scraper).first()
            if not scraper:
                return Response({"error": "Scraper not found"},
                                status=status.HTTP_404_NOT_FOUND)
            scraper_output = ScraperOutputFile.objects.filter(serial=serial_output,
                                                              scraper_file=scraper).first()
            if not scraper_output:
                return Response({"error": "Scraper output not found"},
                                status=status.HTTP_404_NOT_FOUND)
            file_path = scraper_output.file_location + scraper_output.serial + '.csv'
            print('file_path:', file_path)
            if not os.path.exists(file_path):
                return Response({"error": "File not found"},
                                status=status.HTTP_404_NOT_FOUND)
            file = open(file_path, 'rb')
            response = FileResponse(file, as_attachment=True,
                                    filename=f"scraper_output_{serial_output}.csv",
                                    content_type='text/csv',
                                    status=status.HTTP_200_OK)
            return response
        except Exception as e:
            logger.error(f"Error in download_scraper_output: {e}")
            return Response({"error": "Internal server error"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_scraper_status(request, serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({"error": "Unauthorized"},
                                status=status.HTTP_401_UNAUTHORIZED)
            scraper = ScraperUploadFile.objects.filter(serial=serial,
                                                       user=auth_response['user']).first()
            if not scraper:
                return Response({"error": "Scraper upload not found"},
                                status=status.HTTP_404_NOT_FOUND)
            scraper_outputs = ScraperOutputFile.objects.filter(scraper_file=scraper).all()
            output_data = {}
            for output in scraper_outputs:
                output_data[output.serial] = {
                    "file_name": scraper.scraper_name,
                    "status": output.status,
                    "create_date": output.create_date,
                    "update_date": output.update_date,
                    "run_number": output.run_number
                }
            return Response({"scraper_outputs": output_data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in get_scraper_status: {e}")
            return Response({"error": "Internal server error"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_all_scraper_statues(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({"error": "Unauthorized"},
                                status=status.HTTP_401_UNAUTHORIZED)
            scrapers = ScraperUploadFile.objects.filter(user=auth_response['user']).all()
            scraper_data ={}
            for scraper in scrapers:
                scraper_data[scraper.serial] = {
                    "file_name": scraper.scraper_name,
                    "file_description": scraper.scraper_description,
                    "status": scraper.status,
                    "create_date": scraper.create_date,
                    "update_date": scraper.update_date
                }
            return Response({"scrapers": scraper_data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in get_all_scraper_statuses: {e}")
            return Response({"error": "Internal server error"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def trigger_mtg_f2f_scraper(request, serial):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({"error": "Unauthorized"},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            scraper = ScraperUploadFile.objects.filter(serial=serial,
                                                       user=user).first()
            if not scraper:
                return Response({"error": "Scraper upload not found"},
                                status=status.HTTP_404_NOT_FOUND)
            if scraper.status != 'validated':
                return Response({"error": "Scraper file not validated"},
                                status=status.HTTP_400_BAD_REQUEST)
            scraper_run_serial = generate_serial_code(
                config_section='mtg',
                serial_key='mtg_scraper_record_serial_code',
                model=ScraperOutputFile,
                field_name='serial'
            )
            with open('json/directory.json', 'r') as f:
                directory = json.load(f)
            ouput_path = directory['mtg_scraper_output_dir']
            os.makedirs(ouput_path, exist_ok=True)
            last_scrpaper_run = ScraperOutputFile.objects.filter(
                scraper_file=scraper
            ).order_by('-run_number').first()
            if last_scrpaper_run:
                run_number = last_scrpaper_run.run_number + 1
            else:
                run_number = 1
            scraper_run = ScraperOutputFile.objects.create(
                user=user,
                file_name=scraper.file_name,
                serial=scraper_run_serial,
                scraper_file=scraper,
                file_location=ouput_path,
                status='pending',
                create_date=timezone.now(),
                update_date=timezone.now(),
                run_number=run_number
            )
            scraper_run.save()
            return Response({
                "message": "Scraper triggered successfully",
            }, status=status.HTTP_200_OK)   
        except Exception as e:
            logger.error(f"Error in trigger_mtg_f2f_scraper: {e}")
            return Response({"error": "Internal server error"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)