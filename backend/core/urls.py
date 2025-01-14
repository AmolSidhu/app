from django.contrib import admin
from django.urls import path

import user.views
import pictures.views
import streams.views
import videos.views
import management.views
import analytics.views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # User Routes
    path('register/', user.views.register, name='register'),
    path('verification/', user.views.verification, name='verification'),
    path('login/', user.views.login, name='login'),
    path('logout/', user.views.logout, name='logout'),
    path('forgot/password/', user.views.forgot_password, name='forgot_password'),
    path('change/password/', user.views.change_password, name='change_password'),
    path('resend/verification/', user.views.resend_verification, name='resend_verification'),

    # Picture Routes
    path('upload/picture/', pictures.views.upload_picture, name='upload_picture'),
    path('get/picture/<str:album>/', pictures.views.get_picture, name='get_picture'),
    path('get/tags/<str:album_id>/', pictures.views.get_tags, name='get_tags'),
    path('update/picture/', pictures.views.update_picture, name='update_picture'),
    path('get/thumbnail/<str:serial>/', pictures.views.get_thumbnail_image, name='get_thumbnail_image'),
    path('get/picture_image/<str:serial>/', pictures.views.get_picture_image, name='get_picture_image'),
    path('get/picture_data/<str:serial>/', pictures.views.get_picture_data, name='get_picture_data'),
    path('create/album/', pictures.views.create_album, name='create_album'),
    path('get/albums/', pictures.views.get_albums, name='get_albums'),
    path('update/album/<str:serial>/', pictures.views.update_album, name='update_album'),
    path('create/custom_album/', pictures.views.create_custom_album, name='create_custom_album'),
    path('add/image/custom_album/<str:album_serial>/<str:image_serial>/', pictures.views.add_image_to_custom_album, name='add_image_to_custom_album'),
    path('get/custom_albums/', pictures.views.get_custom_album, name='get_custom_album'),
    path('get/custom_album_images/<str:serial>/', pictures.views.get_custom_album_images, name='get_custom_album_images'),
    path('update/custom_album/', pictures.views.update_custom_album, name='update_custom_album'),
    path('add/image_favourites/<str:serial>/', pictures.views.add_to_favourites, name='add_to_faviourites'),
    path('get/favourite_images/', pictures.views.get_favourites, name='get_favourites'),
    path('delete/favorite_image/', pictures.views.remove_from_favourites, name='remove_from_favourites'),
    path('delete/custom_album/<str:album_serial>/<str:image_serial>/', pictures.views.remove_from_custom_album, name='remove_from_custom_album'),
    path('generate/picture_query/', pictures.views.generate_picture_query, name='generate_picture_query'),
    path('fetch/picture_query/<str:search_id>/', pictures.views.get_picture_query, name='fetch_picture_query'),
    
    # Stream Routes
    path('get/video_stream/<str:serial>/<str:permission>/', streams.views.get_video_stream, name='get_video_stream'),
    path('get/video_history/<str:serial>/', streams.views.get_video_history, name='get_video_history'),
    path('update/playback_time/<str:serial>/', streams.views.update_playback_time, name='update_playback_time'),
    
    # Video Routes
    path('upload/video/', videos.views.upload_video, name='upload_video'),
    path('upload/batch_video/', videos.views.batch_video_upload, name='batch_video_upload'),
    path('get/videos/', videos.views.get_videos, name='get_videos'),
    path('get/video_thumbnail/<str:serial>/', videos.views.get_video_thumbnail, name='get_video_thumbnail'),
    path('get/video_data/<str:serial>/', videos.views.get_video_data, name='get_video_data'),
    path('get/episode_data/<str:serial>/<int:season>/', videos.views.episode_data, name='get_episode_data'),
    path('get/genres/', videos.views.get_genres, name='get_genres'),
    path('get/videos_by_genre/<str:genre>/', videos.views.get_videos_by_genre, name='get_videos_by_genre'),
    path('get/recently_viewed_videos/', videos.views.recently_viewed_videos, name='get_recently_viewed_videos'),
    path('get/videos_by_search/<str:search>/', videos.views.get_videos_by_search, name='get_videos_by_search'),
    path('generate/video_query/', videos.views.generate_video_search, name='generate_video_search'),
    path('fetch/video_search/<str:search_id>/', videos.views.get_video_query, name='fetch_video_query'),
    
    # Management Routes
    path('import_identifier_api/', management.views.import_identifier_api, name='import_identifier_api'),
    path('update_episode_record/<int:season>/<int:episode>/', management.views.update_episode_record, name='update_episode_record'),
    path('delete_video_record/<str:serial>/', management.views.delete_video_record, name='delete_video_record'),
    path('delete_episode_record/<str:serial>/<int:season>/<int:episode>/', management.views.delete_episode_record, name='delete_episode_record'),
    path('delete_season_records/<str:serial>', management.views.delete_season_records, name='delete_season_records'),
    path('change_email/', management.views.change_email, name='change_email'),
    path('change_username/', management.views.change_username, name='change_username'),
    path('delete_account/', management.views.delete_account, name='delete_account'),
    path('get/video_list/', management.views.get_video_list, name='get_video_list'),
    path('update/video_record/<str:serial>/', management.views.update_video_record, name='update_video_record'),
    path('get/full_video_record/<str:serial>/', management.views.get_full_video_record, name='get_full_video_record'),
    
    # Analytics Routes
    path('upload/data_source/', analytics.views.upload_data_source, name='upload_data_source'),
    path('create/dashboard/', analytics.views.create_dashboard, name='create_dashboard'),
    path('create/dashboard_item/<str:serial>', analytics.views.create_dashboard_item, name='create_dashboard_item'),
    path('get/dashboard/', analytics.views.get_dashboard, name='get_dashboard'),
    path('get/dashboard_item/<str:serial>/', analytics.views.get_dashboard_item, name='get_dashboard_item'),
]
