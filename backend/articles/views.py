from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status

import logging
import json
import os

from functions.auth_functions import auth_check
from functions.serial_default_generator import generate_serial_code

from .models import MainArticle, MassUploadFiles, ArticleTags, MyArticleList, MyArticleListRecords
from .queries import get_article_tag_search_query, get_article_title_search_query

logger = logging.getLogger(__name__)

@api_view(['POST'])
def create_single_article(request):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            serial = generate_serial_code(
                config_section='articles',
                serial_key='main_article_serial_code',
                model=MainArticle,
                field_name='serial'
            )
            new_article = MainArticle(
                serial=serial,
                user=auth['user'],
                title=request.data.get('title', 'Untitled'),
                content=request.data.get('content', ''),
                create_date=timezone.now(),
                update_date=timezone.now()
            )
            new_article.save()
            tags = request.data.get('tags', [])
            for tag in tags:
                serial = generate_serial_code(
                    config_section='articles',
                    serial_key='article_tag_serial_code',
                    model=ArticleTags,
                    field_name='serial'
                )
                article_tag = ArticleTags(
                    serial=serial,
                    main_article=new_article,
                    article=new_article,
                    tag=tag
                )
                article_tag.save()
            return Response({"message": "Article created successfully"},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creating single article: {e}")
            return Response({"message": "Failed to create article"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def create_multiple_articles(request):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            return Response({"message": "Articles uploaded successfully"},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creating multiple articles: {e}")
            return Response({"message": "Failed to create articles"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['POST'])
def upload_article_files(request):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            file = request.FILES.get('file')
            file_extension = os.path.splitext(file.name)[-1].lower()
            if file_extension not in ['.txt', '.md', '.json', '.html', '.jsonl']:
                return Response({"message": "Unsupported file type"},
                                status=status.HTTP_400_BAD_REQUEST)
            with open('json/directory.json', 'r') as f:
                directory = json.load(f)
            article_directory = directory['article_file_upload_dir']
            if not os.path.exists(article_directory):
                os.makedirs(article_directory)
            serial = generate_serial_code(
                config_section='articles',
                serial_key='file_serial_code',
                model=MassUploadFiles,
                field_name=''
            )
            uploaded_file = MassUploadFiles(
                serial=serial,
                user=auth['user'],
                file_location=article_directory,
                file_extension=file_extension,
                file_status='uploaded'
            )
            uploaded_file.save()
            write_path = os.path.join(article_directory, serial + file_extension)
            with open(write_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            return Response({"message": "Article files uploaded successfully"},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error uploading article files: {e}")
            return Response({"message": "Failed to upload article files"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def search_articles(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            title_query = request.GET.get('title', '')
            query_tags = []
            tags = request.GET.get('tags', '')
            if tags:
                query_tags_ = tags.split(',')
                query_tags = [tag.strip() for tag in query_tags_ if tag.strip()]
                
            if request.Get.get('query_type') == 'title':
                pass
            elif request.GET.get('query_type') == 'tag':
                pass
            elif request.GET.get('query_type') == 'both':
                pass
            return Response({"message": "Search completed successfully"},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error searching articles: {e}")
            return Response({"message": "Failed to search articles"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['POST'])
def create_articles_list(request):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            serial = generate_serial_code(
                config_section='articles',
                serial_key='article_user_list_serial_code',
                model=MyArticleList,
                field_name='serial'
            )
            new_article_list = MyArticleList(
                serial=serial,
                user=auth['user'],
                my_article_list_name=request.data.get('list_name', 'New List'),
                my_article_list_description=request.data.get('list_description', ''),
                create_date=timezone.now(),
                update_date=timezone.now()
            )
            new_article_list.save()
            return Response({"message": "Articles list created successfully"},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creating articles list: {e}")
            return Response({"message": "Failed to create articles list"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def add_article_to_my_list(request, article_serial, list_serial):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            article = MainArticle.objects.filter(serial=article_serial).first()
            if not article:
                return Response({"message": "Article not found"},
                                status=status.HTTP_404_NOT_FOUND)
            my_list = MyArticleList.objects.filter(serial=list_serial,
                                                   user=auth['user']).first()
            if not my_list:
                return Response({"message": "My Article List not found"},
                                status=status.HTTP_404_NOT_FOUND)
            serial = generate_serial_code(
                config_section='articles',
                serial_key='articles_user_list_record_serial_code',
                model=MyArticleListRecords,
                field_name='serial'
            )
            new_list_record = MyArticleListRecords(
                serial=serial,
                user=auth['user'],
                main_article=article,
                created_at=timezone.now()
            )
            new_list_record.save()
            return Response({"message": "Article added to your list successfully"},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error adding article to my list: {e}")
            return Response({"message": "Failed to add article to your list"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def update_article(request, article_serial):
    if request.method == 'PATCH':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            article = MainArticle.objects.filter(serial=article_serial,
                                                 user=auth['user']).first()
            if not article:
                return Response({"message": "Article not found"},
                                status=status.HTTP_404_NOT_FOUND)
            title = request.data.get('title')
            content = request.data.get('content')
            if title:
                article.title = title
            if content:
                article.content = content
            article.update_date = timezone.now()
            article.save()
            return Response({"message": "Article updated successfully"},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error updating article: {e}")
            return Response({"message": "Failed to update article"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def delete_article(request, article_serial):
    if request.method == 'DELETE':
        try:
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            article = MainArticle.objects.filter(serial=article_serial,
                                                 user=auth['user']).first()
            if not article:
                return Response({"message": "Article not found"},
                                status=status.HTTP_404_NOT_FOUND)
            article.delete()
            return Response({"message": "Article deleted successfully"},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error deleting article: {e}")
            return Response({"message": "Failed to delete article"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)