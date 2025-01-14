"""
WSGI config for core project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()

from . import runner as run

run.start_check_corruption_temp()
run.start_convert_video()
run.start_check_corruption_data()
run.start_imdb_data()
run.start_identifier_check()
run.start_audio_profile()
run.start_visual_profile()
run.start_completed_processing()
run.start_failed_or_error_processing()
run.start_add_identifiers()
run.start_create_json_record()
run.start_check_existing_genres()
run.start_check_series_data()
run.start_video_marked_for_deletion()
run.start_video_marked_for_deletion()
run.start_delete_video_search()
run.start_delete_picture_query()
