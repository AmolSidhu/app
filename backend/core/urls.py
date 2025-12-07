from django.contrib import admin
from django.urls import path

import user.views
import pictures.views
import streams.views
import videos.views
import management.views
import analytics.views
import youtube.views
import music.views
import articles.views
import files.views
import mtg.views
import admins.views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # User Routes
    path('register/', user.views.register, name='register'),
    path('verification/', user.views.verification, name='verification'),
    path('login/', user.views.login, name='login'),
    path('logout/', user.views.logout, name='logout'),
    path('forgot/password/', user.views.forgot_password, name='forgot_password'),
    path('change/password/', user.views.change_password, name='change_password'),
    path('resend/forgot_password/', user.views.resend_forgot_password, name='resend_forgot_password'),
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
    path('create/custom_album/', pictures.views.create_custom_image_album, name='create_custom_image_album'),
    path('add/image/custom_album/<str:album_serial>/<str:image_serial>/', pictures.views.add_image_to_custom_album, name='add_image_to_custom_album'),
    path('get/custom_albums/', pictures.views.get_custom_image_album, name='get_custom_image_album'),
    path('get/custom_album_images/<str:serial>/', pictures.views.get_custom_album_images, name='get_custom_album_images'),
    path('update/custom_album/', pictures.views.update_custom_image_album, name='update_custom_image_album'),
    path('update/image_favourites/<str:serial>/', pictures.views.update_image_favourites, name='update_image_favourites'),
    path('get/favourite_images/', pictures.views.get_image_favourites, name='get_image_favourites'),
    path('delete/favorite_image/', pictures.views.remove_from_image_favourites, name='remove_from_image_favourites'),
    path('delete/image/custom_album/<str:album_serial>/<str:image_serial>/', pictures.views.remove_from_custom_image_album, name='remove_from_custom_image_album'),
    path('generate/picture_query/', pictures.views.generate_picture_query, name='generate_picture_query'),
    path('fetch/picture_query/<str:search_id>/', pictures.views.get_picture_query, name='fetch_picture_query'),

    # Stream Routes
    path('get/video_stream/<str:serial>/<str:permission>/', streams.views.get_video_stream, name='get_video_stream'),
    path('get/video_history/<str:serial>/', streams.views.get_video_history, name='get_video_history'),
    path('update/playback_time/<str:serial>/', streams.views.update_playback_time, name='update_playback_time'),
    path('get/next_previous_episode/<str:video_serial>/', streams.views.get_next_previous_episode, name='get_next_previous_episode'),
    path('get/video_suggestions/<str:video_serial>/', streams.views.get_video_suggestions, name='get_video_suggestions'),

    # Video Routes
    path('upload/video/', videos.views.upload_video, name='upload_video'),
    path('upload/batch_video/', videos.views.batch_video_upload, name='batch_video_upload'),
    path('get/series_serials/', videos.views.get_series_serials, name='get_series_serials'),
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
    path('create/custom_video_list/', videos.views.create_custom_video_list, name='create_custom_video_list'),
    path('add/video/custom_list/<str:video_serial>/<str:list_serial>/', videos.views.add_video_to_custom_list, name='add_video_to_custom_list'),
    path('delete/video/custom_list/<str:video_serial>/<str:list_serial>/', videos.views.remove_video_from_custom_list, name='remove_video_from_custom_list'),
    path('get/custom_video_lists/', videos.views.get_custom_video_lists, name='get_custom_video_lists'),
    path('get/custom_list_videos/<str:list_serial>/', videos.views.get_custom_video_list_records, name='get_custom_video_list_records'),
    path('update/favourite_videos/<str:serial>/', videos.views.update_video_favourites, name='update_video_favourites'), 
    path('get/favourite_videos/', videos.views.get_favourite_videos, name='get_favourite_videos'),
    path('create/video_request/', videos.views.create_video_request, name='create_video_request'),
    path('get/video_requests/', videos.views.get_video_requests, name='get_video_requests'),
    path('get/series_serials/', videos.views.get_series_serials, name='get_series_serials'),

    # Management Routes
    path('import_identifier_api/', management.views.import_identifier_api, name='import_identifier_api'),
    path('update_episode_record/<int:season>/<int:episode>/', management.views.update_episode_record, name='update_episode_record'),
    path('delete_video_record/<str:serial>/', management.views.delete_video_record, name='delete_video_record'),
    path('delete_episode_record/<str:serial>/<int:season>/<int:episode>/', management.views.delete_episode_record, name='delete_episode_record'),
    path('delete_season_records/<str:serial>', management.views.delete_season_records, name='delete_season_records'),
    path('change/password/', management.views.change_password, name='change_password'),
    path('change/email/', management.views.change_email, name='change_email'),
    path('change/username/', management.views.change_username, name='change_username'),
    path('delete_account/', management.views.delete_account, name='delete_account'),
    path('get/editing_video_list/', management.views.get_editing_video_list, name='get_editing_video_list'),
    path('get/single_video_record/<str:serial>/', management.views.get_single_video_record, name='get_single_video_record'),
    path('get/full_video_record/<str:serial>/', management.views.get_full_video_record, name='get_full_video_record'),
    path('get/episode_records/<str:serial>/<int:season>/', management.views.get_episode_records, name='get_episode_records'),
    path('get/picture_record/<str:serial>/', management.views.get_picture_record, name='get_picture_record'),
    path('update/picture_record/<str:serial>/', management.views.update_picture_record, name='update_picture_record'),
    path('update/video_record/<str:serial>/', management.views.update_video_record, name='update_video_record'),
    path('update/video_episode/<str:serial>/', management.views.update_video_episode, name='update_video_episodes'),
    path('get/server/metadata/', management.views.get_server_metadata, name='get_server_metadata'),
    path('get/server/patch_data/', management.views.get_server_patch_data, name='get_server_patch_data'),

    # Youtube Routes
    path('create/youtube_playlist/', youtube.views.create_youtube_playlist, name='create_youtube_playlist'),
    path('upload/youtube_video/', youtube.views.upload_youtube_video, name='upload_youtube_video'),
    path('add/video/youtube_playlist/', youtube.views.add_video_to_youtube_playlist, name='add_video_to_playlist'),
    path('get/youtube_playlists/', youtube.views.get_youtube_playlists, name='get_youtube_playlists'),
    path('get/playlist_videos/<str:playlist_serial>/', youtube.views.get_playlist_videos, name='get_playlist_videos'),
    path('get/youtube_thumbnail/<str:serial>/', youtube.views.get_youtube_thumbnail, name='get_youtube_thumbnail'),
    path('watch/youtube_video/<str:serial>/<str:token>/', youtube.views.watch_youtube_video, name='watch_youtube_video'),
    path('update/youtube_playback_time/<str:serial>/', youtube.views.update_youtube_playback_time, name='update_youtube_playback_time'),
    path('delete/youtube_video_from_playlist/<str:video_serial>/<str:playlist_serial>/', youtube.views.delete_youtube_video_from_playlist, name='delete_video_from_youtube_playlist'),
    path('get/youtube_video_stream/<str:serial>/<str:permission>/', youtube.views.get_youtube_video_stream, name='get_youtube_video_stream'),
    path('update/youtube_playback_time/<str:serial>/', youtube.views.update_youtube_playback_time, name='update_youtube_playback_time'),

    # Analytics Routes
    path('upload/data_source/', analytics.views.upload_data_source, name='upload_data_source'),
    path('update/data_source/<str:serial>/', analytics.views.update_data_source, name='update_data_source'),
    path('update/data_source_lines/<str:serial>/', analytics.views.update_data_source_lines, name='update_data_source_lines'),
    path('reset/data_source_lines/<str:serial>/', analytics.views.reset_data_source_lines, name='reset_data_source_lines'),
    path('get/data_source_cleaning_methods/<str:serial>/', analytics.views.get_data_source_cleaning_methods, name='get_data_source_cleaning_methods'),
    path('update/data_source_cleaning_methods/<str:serial>/', analytics.views.update_data_source_cleaning_methods, name='update_data_source_cleaning_methods'),
    path('get/data_source_lines/<str:serial>/', analytics.views.get_data_source_lines, name='get_data_source_lines'),
    path('create/dashboard/', analytics.views.create_dashboard, name='create_dashboard'),
    path('create/dashboard_item/<str:serial>/', analytics.views.create_dashboard_item, name='create_dashboard_item'),
    path('create/dashboard_item_data/<str:dashboard_serial>/<str:dashboard_item_serial>/', analytics.views.create_dashboard_item_data, name='create_dashboard_item_data'),
    path('get/dashboard_item_serials/<str:dashboard_serial>/', analytics.views.get_dashboard_item_serials, name='get_dashboard_item_serials'),
    path('get/dashboard_item/<str:dashboard_serial>/<str:dashboard_item_serial>/', analytics.views.get_dashboard_item, name='get_dashboard_item'),
    path('get/dashboard_item_data/<str:dashboard_serial>/<str:dashboard_item_serial>/', analytics.views.get_dashboard_item, name='get_dashboard_item_data'),
    path('update/dashboard_item/<str:dashboard_serial>/<str:dashboard_item_serial>/', analytics.views.update_dashboard_item, name='update_dashboard_item'),
    path('delete/dashboard_item/<str:dashboard_serial>/<str:dashboard_item_serial>/', analytics.views.delete_dashboard_item, name='delete_dashboard_item'),
    path('delete/dashboard/<str:serial>/', analytics.views.delete_dashboard, name='delete_dashboard'),
    path('get/data_sources/', analytics.views.get_data_sources, name='get_data_sources'),
    path('get/cleaned_data_sources/', analytics.views.get_cleaned_data_sources, name='get_cleaned_data_sources'),
    path('get/data_source_detials/<str:serial>/', analytics.views.get_data_source_details, name='get_data_source_details'),
    path('get/dashboards/', analytics.views.get_dashboards, name='get_dashboards'),
    path('get/dashboard/<str:serial>', analytics.views.get_dashboard, name='get_dashboard'),
    path('get/dashboard_items/<str:serial>/', analytics.views.get_dashboard_items, name='get_dashboard_item'),
    path('get/dashboard_item_output/<str:serial>/<int:item_order>/', analytics.views.get_dashboard_item_output, name='get_dashboard_item_output'),
    path('setup/report/', analytics.views.setup_report, name='setup_report'),
    path('create/report_settings/<str:serial>/', analytics.views.create_report_settings, name='create_report_settings'),
    path('get/report_settings/<str:serial>/', analytics.views.get_report_settings, name='get_report_settings'),
    path('update/report_settings/<str:serial>/', analytics.views.update_report_settings, name='update_report_settings'),
    path('delete/report_settings/<str:serial>/', analytics.views.delete_report_settings, name='delete_report_settings'),

    # Music Routes
    path('upload/music_links/', music.views.upload_music_links, name='upload_music_links'),
    path('get/music_albums/', music.views.get_music_albums, name='get_music_albums'),
    path('get/music_album_data/<str:serial>/', music.views.get_music_album_data, name='get_music_album_data'),
    path('get/music_tracks/<str:serial>/', music.views.get_music_tracks, name='get_music_tracks'),
    path('get/artist_thumbnail/<str:serial>/', music.views.get_artist_thumbnail, name='get_artist_thumbnail'),
    path('get/album_thumbnail/<str:serial>/', music.views.get_album_thumbnail, name='get_album_thumbnail'),
    path('get/track_data/<str:serial>/', music.views.get_track_data, name='get_track_data'),
    path('get/track_preview/<str:serial>/', music.views.get_track_preview, name='get_track_preview'),
    path('get/artist_data/', music.views.get_artist_data, name='get_artist_data'),
    
    # Article Routes
    path('create/single_article/', articles.views.create_single_article, name='create_single_article'),
    path('create/multiple_articles/', articles.views.create_multiple_articles, name='create_multiple_articles'),
    path('upload/article_files/', articles.views.upload_article_files, name='upload_article_files'),
    path('search/articles/', articles.views.search_articles, name='search_articles'),
    path('create/articles_list/', articles.views.create_articles_list, name='create_articles_list'),
    path('add/articles_to_my_list/<str:serial>/', articles.views.add_article_to_my_list, name='add_articles_to_my_list'),
    path('update/article/<str:serial>/', articles.views.update_article, name='update_article'),
    path('delete/article/<str:serial>/', articles.views.delete_article, name='delete_article'),
    
    # File Routes
    path('create/upload_folder/', files.views.create_upload_folder, name='create_upload_folder'),
    path('upload/file/', files.views.upload_file, name='upload_file'),
    path('get/files/', files.views.get_files, name='get_files'),
    path('get/folders/', files.views.get_folders, name='get_folders'),
    path('get/folder_files/<str:folder_serial>/', files.views.get_folder_files, name='get_folder_files'),
    path('get/folder_data/<str:folder_serial>/', files.views.get_folder_data, name='get_folder_data'),
    path('get/file/<str:file_id>/', files.views.get_file, name='get_file'),
    path('get/downloaded_file/<str:file_id>/<str:share_code>/', files.views.get_downloaded_file, name='get_downloaded_file'),
    path('get/folder_downloaded_files/<str:folder_serial>/<str:share_code>/', files.views.get_folder_downloaded_files, name='get_folder_downloaded_files'),
    path('get/file_share_data/<str:file_id>/', files.views.get_file_share_data, name='get_file_share_data'),
    path('update/file_share_status/<str:file_id>/', files.views.update_file_share_status, name='update_file_share_status'),
    path('get/folder_share_data/<str:folder_serial>/', files.views.get_folder_share_data, name='get_folder_share_data'),
    path('update/folder_share_status/<str:folder_serial>/', files.views.update_folder_share_status, name='update_folder_share_status'),
    path('get/file_share_link/<str:file_id>/', files.views.get_file_share_link, name='get_file_share_link'),
    path('get/folder_share_link/<str:folder_serial>/', files.views.get_folder_share_link, name='get_folder_share_link'),
    path('delete/file/<str:file_id>/', files.views.delete_file, name='delete_file'),
    path('delete/folder/<str:folder_serial>/', files.views.delete_folder, name='delete_folder'),
    
    # MTG Routes
    path('create/scraper/', mtg.views.create_new_scraper, name='create_new_scraper'),
    path('get/default_template/', mtg.views.get_default_template, name='get_default_template'),
    path('download/scraper_output/<str:serial_scraper>/<str:serial_output>/', mtg.views.get_download_scraper_output, name='get_download_scraper_output'),
    path('get/scraper_status/<str:serial>/', mtg.views.get_scraper_status, name='get_scraper_status'),
    path('get/all_scraper_statuses/', mtg.views.get_all_scraper_statues, name='get_all_scraper_statuses'),
    path('trigger/mtg_f2f_scraper/<str:serial>/', mtg.views.trigger_mtg_f2f_scraper, name='trigger_mtg_f2f_scraper'),
    
    # Admins Routes
    path('admins/login/', admins.views.admin_login, name='admin_login'),
    path('admins/video_request_options/', admins.views.video_request_options, name='video_request_options'),
    path('admins/video_requests/<str:status_filter>/', admins.views.video_requests, name='video_requests'),
    path('admins/review_video_request/<str:serial>/', admins.views.review_video_request, name='review_video_request'),
]
