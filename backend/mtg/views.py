from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import FileResponse, HttpResponse
from django.utils import timezone
from urllib.parse import unquote
from rest_framework import status
from django.db import connection

import logging
import json
import os
import io

from functions.check_functions.auth_functions import auth_check
from functions.check_functions.serial_default_generator import generate_serial_code
from functions.view_functions.create_default_mtg_view import create_default_mtg_view
from functions.view_functions.magic_param_sorter import magic_param_sorter

from .models import MagicCards, ScraperUploadFile, ScraperOutputFile, MagicViewFields, MagicCardLegalities, MagicCardPrices
from .query_fields import magic_cards_query_fields, magic_cards_query_operators, create_where_clause
from .queries import get_magic_card_data_query, magic_card_data_query

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
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({"error": "Unauthorized"},
                                status=status.HTTP_401_UNAUTHORIZED)
            base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            with open('json/templates_dir.json', 'r') as f:
                templates_dir = json.load(f)
            template = templates_dir['mtg']['default_template']
            template_path = os.path.join(base, template)
            if not os.path.exists(template_path):
                return Response({"error": f"Template file not found at {template_path}"},
                                status=status.HTTP_400_BAD_REQUEST)
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
            return Response({"message": "Scraper triggered successfully",},
                            status=status.HTTP_200_OK)   
        except Exception as e:
            logger.error(f"Error in trigger_mtg_f2f_scraper: {e}")
            return Response({"error": "Internal server error"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['GET'])
def get_magic_card_view_options(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({"error": "Unauthorized"}, 
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            get_view_options = MagicViewFields.objects.filter(user=user).first()
            if not get_view_options:
                try:
                    create_view = create_default_mtg_view(user)
                except Exception as e:
                    return Response({"error": "Internal server error"},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                get_view_options = MagicViewFields.objects.filter(user=user).first()
            data = {}
            data['active_fields'] = get_view_options.active_fields
            data['active_fields_names'] = get_view_options.active_fields_names
            return Response({"data": data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in retrieving magic cards: {e}")
            return Response({"error": "Internal server error"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['GET'])
def get_magic_card_view_options_fields(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({"error": "Unauthorized"},
                                status=status.HTTP_401_UNAUTHORIZED)
            get_view_options_fields = MagicViewFields.objects.filter(
                user=auth_response['user']).first()
            if not get_view_options_fields:
                logger.error(f"Magic card view options fields not found")
                return Response({"error": "Magic card view options fields not found"},
                                status=status.HTTP_400_BAD_REQUEST)
            with open('json/views_default_options.json', 'r') as f:
                default_options = json.load(f)
            data = {}
            for default_option in default_options:
                field_name = default_options[default_option].get("field_name")
                if field_name:
                    data[field_name] = default_options[default_option]
            return Response({"message": "Magic card view options fields retrieved successfully",
                             "data": data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in retrieving magic card view options fields: {e}")
            return Response({"error": "Internal server error"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def update_magic_card_view_options(request):
    if request.method == 'PATCH':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({"error": "Unauthorized"},
                                status=status.HTTP_401_UNAUTHORIZED)
            column_view = MagicViewFields.objects.filter(user=auth_response['user']).first()
            if not column_view:
                return Response({"error": "Magic card view options not found"},
                                status=status.HTTP_400_BAD_REQUEST)
            new_active_fields = request.data.get('active_fields')
            if not new_active_fields:
                return Response({"error": "No active fields provided"},
                                status=status.HTTP_400_BAD_REQUEST)
            with open('json/views_default_options.json', 'r') as f:
                default_options = json.load(f)
            active_field_names = []
            for field in new_active_fields:
                for key, option in default_options.items():
                    if option.get("field_name") == field:
                        active_field_names.append(option.get("user_view"))
                        break
            column_view.active_fields = new_active_fields
            column_view.active_fields_names = active_field_names
            column_view.save()
            return Response({"message": "Magic card view options updated successfully"},
                            status=status.HTTP_200_OK) 
        except Exception as e:
            logger.error(f"Error in updating magic card view options: {e}")
            return Response({"error": "Internal server error"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_magic_card_all_view_options(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({"error": "Unauthorized"},
                                status=status.HTTP_401_UNAUTHORIZED)
            column_view = MagicViewFields.objects.filter(
                user=auth_response['user']).first()
            if not column_view:
                return Response({"error": "Magic card view options not found"},
                                status=status.HTTP_400_BAD_REQUEST)
            active_fields = column_view.active_fields
            if isinstance(active_fields, str):
                active_fields = [data_field.strip() for data_field in active_fields.split(
                    ',') if data_field.strip()]
            used_options = []
            unused_options = []
            with open('json/views_default_options.json', 'r') as f:
                default_options = json.load(f)
            default_columns = default_options['magic_cards']
            for column_key in default_columns:
                column = default_columns[column_key]
                if not isinstance(column, dict):
                    continue
                data = {
                    "field_name": column.get('field_name', column_key),
                    "user_view":  column.get('user_view', column.get('field_name', column_key))
                }
                if data["field_name"] in active_fields:
                    used_options.append(data)
                else:
                    unused_options.append(data)
            return Response({"message": "Magic card view options retrieved successfully",
                             "used_options": used_options,
                             "unused_options": unused_options},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in getting all view options: {e}", exc_info=True)
            return Response({"error": "Internal server error"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_magic_card_view_filters(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({"error": "Unauthorized"},
                                status=status.HTTP_401_UNAUTHORIZED)
            filter_record = MagicViewFields.objects.filter(
                user=auth_response['user']).first()
            if not filter_record:
                return Response({"error": "Magic card view filters not found"},
                                status=status.HTTP_400_BAD_REQUEST)
            with open('json/views_default_options.json', 'r') as f:
                default_options = json.load(f)
            data = default_options['magic_cards']
            return Response({"message": "Magic card view filters retrieved successfully",
                             "data": data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in getting magic card view filters: {e}")
            return Response({"error": "Internal server error"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['DELETE'])
def reset_magic_card_view_options(request): 
    if request.method == 'DELETE':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({"error": "Unauthorized"},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = auth_response['user']
            column_view = MagicViewFields.objects.filter(user=user).first()
            if not column_view:
                return Response({"error": "Magic card view options not found"},
                                status=status.HTTP_400_BAD_REQUEST)
            column_view.delete()
            try:
                create_view = create_default_mtg_view(user)
            except Exception as e:
                logger.error(f"Error in creating default view options: {e}")
                return Response({"error": "Internal server error"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({"message": "Magic card view options reset to default successfully"},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in resetting magic card view options: {e}")
            return Response({"error": "Internal server error"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_magic_card_data(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({"error": "Unauthorized"},
                                status=status.HTTP_401_UNAUTHORIZED)
            raw_sql = request.query_params.get("sql", "")
            page = int(request.query_params.get('page', 1))
            limit = int(request.query_params.get('limit', 50))
            offset = (page - 1) * limit
            where_clause, where_params = create_where_clause(raw_sql)
            query = magic_card_data_query(where_clause)
            with connection.cursor() as cursor:
                cursor.execute(query, where_params + [limit + 1, offset])
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                has_more = len(rows) > limit
                data = [dict(zip(columns, row)) for row in rows[:limit]]
            return Response({ 
                "message": "Magic card data retrieved successfully",
                "data": data,
                "has_more": has_more,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in retrieving magic card data: {str(e)}")
            return Response({"error": "Internal server error"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_magic_card_image(request, serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({"error": "Unauthorized"},
                                status=status.HTTP_401_UNAUTHORIZED)
            card_record = MagicCards.objects.filter(card_id=serial).first()
            if not card_record:
                return Response({"error": "Magic card not found"},
                                status=status.HTTP_404_NOT_FOUND)
            card_back_param = request.query_params.get('card_back')
            if card_back_param is None:
                return Response({"error": "Parameter 'card_back' is required"},
                                status=status.HTTP_400_BAD_REQUEST)
            card_back = card_back_param.lower()
            if card_back == 'true':
                if not card_record.back_exists:
                    return Response({"error": "Magic card back image not found"},
                                    status=status.HTTP_404_NOT_FOUND)
                full_card_path = os.path.join(
                    card_record.image_dir,
                    f"{card_record.back_serial}.png"
                )
                card_serial = card_record.back_serial
            elif card_back == 'false':
                if not card_record.image_added:
                    return Response({"error": "Magic card image not found"},
                                    status=status.HTTP_404_NOT_FOUND)
                full_card_path = os.path.join(
                    card_record.image_dir,
                    f"{card_record.card_id}.png"
                )
                card_serial = card_record.card_id
            else:
                return Response({"error": "Parameter 'card_back' must be 'true' or 'false'"},
                                status=status.HTTP_400_BAD_REQUEST)
            if not os.path.exists(full_card_path):
                return Response({"error": "Magic card image file not found"},
                                status=status.HTTP_404_NOT_FOUND)
            with open(full_card_path, 'rb') as f:
                image_data = f.read()
            response = HttpResponse(image_data, content_type='image/png', status=status.HTTP_200_OK)
            response['back-exists'] = 'true' if card_record.back_exists else 'false'
            return response
        except Exception as e:
            logger.error(f"Error retrieving magic card image: {e}")
            return Response({"error": "Internal server error"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_magic_card_json(request, serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({"error": "Unauthorized"},
                                status=status.HTTP_401_UNAUTHORIZED)
            card_record = MagicCards.objects.filter(card_id=serial).first()
            if not card_record:
                return Response({"error": "Magic card not found"},
                                status=status.HTTP_404_NOT_FOUND)
            json_file = card_record.json_dir + card_record.card_id + '.json'
            if not os.path.exists(json_file):
                return Response({"error": "Magic card json file not found"},
                                status=status.HTTP_404_NOT_FOUND)
            with open(json_file, 'r') as f:
                card_json = json.load(f)
            return Response({"message": "Magic card json retrieved successfully",
                             "data": card_json},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in retrieving magic card json: {e}")
            return Response({"error": "Internal server error"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_magic_card_legalities(request, serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({"error": "Unauthorized"},
                                status=status.HTTP_401_UNAUTHORIZED)
            legality_record = MagicCardLegalities.objects.filter(card=serial).first()
            if not legality_record:
                return Response({"error": "Magic card legalities not found"},
                                status=status.HTTP_404_NOT_FOUND)
            data = {
                "duel": legality_record.duel,
                "brawl": legality_record.brawl,
                "penny": legality_record.penny,
                "predh": legality_record.predh,
                "future": legality_record.future,
                "legacy": legality_record.legacy,
                "modern": legality_record.modern,
                "pauper": legality_record.pauper,
                "alchemy": legality_record.alchemy,
                "pioneer": legality_record.pioneer,
                "vintage": legality_record.vintage,
                "historic": legality_record.historic,
                "standard": legality_record.standard,
                "timeless": legality_record.timeless,
                "commander": legality_record.commander,
                "gladiator": legality_record.gladiator,
                "oldschool": legality_record.oldschool,
                "premodern": legality_record.premodern,
                "oathbreaker": legality_record.oathbreaker,
                "standardbrawl": legality_record.standardbrawl,
                "paupercommander": legality_record.paupercommander,
            }
            return Response({"message": "Magic card legalities retrieved successfully",
                             "data": data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in retrieving magic card legalities: {e}")
            return Response({"error": "Internal server error"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['GET'])
def get_magic_card_prices(request, serial):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth_response = auth_check(token)
            if 'error' in auth_response:
                return Response({"error": "Unauthorized"},
                                status=status.HTTP_401_UNAUTHORIZED)
            price_record = MagicCardPrices.objects.filter(card=serial).first()
            if not price_record:
                return Response({"error": "Magic card prices not found"},
                                status=status.HTTP_404_NOT_FOUND)
            data = {
                "Euro": price_record.eur_price,
                "Tickets": price_record.tix_price,
                "USD": price_record.usd_price,
                "Euro Foil": price_record.eur_foil_price,
                "USD Foil": price_record.usd_foil_price,
                "USD Etched": price_record.usd_etched_price,
            }
            return Response({"message": "Magic card prices retrieved successfully",
                             "data": data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in retrieving magic card price: {e}")
            return Response({"error": "Internal server error"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)