from apscheduler.schedulers.background import BackgroundScheduler

import functions.jobs as job

def start_check_corruption_temp():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job.check_corruption_temp, 'interval', minutes=1)
    scheduler.start()
    
def start_convert_video():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job.convert_video, 'interval', minutes=1)
    scheduler.start()
    
def start_check_corruption_data():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job.check_corruption_data, 'interval', minutes=1)
    scheduler.start()
    
def start_imdb_data():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job.imdb_data, 'interval', minutes=1)
    scheduler.start()

def start_identifier_check():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job.identifier_check, 'interval', minutes=1)
    scheduler.start()
    
def start_audio_profile():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job.audio_profile, 'interval', minutes=1)
    scheduler.start()
    
def start_visual_profile():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job.visual_profile, 'interval', minutes=1)
    scheduler.start()

def start_completed_processing():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job.completed_processing, 'interval', minutes=1)
    scheduler.start()

def start_failed_or_error_processing():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job.failed_or_error_processing, 'interval', minutes=1)
    scheduler.start()

def start_add_identifiers():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job.add_identifiers, 'interval', minutes=1)
    scheduler.start()

def start_create_json_record():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job.create_json_record, 'interval', minutes=1)
    scheduler.start()

def start_check_existing_genres():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job.check_existing_genres, 'interval', minutes=1)
    scheduler.start()

def start_check_series_data():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job.check_series_data, 'interval', minutes=1)
    scheduler.start()

def start_video_marked_for_deletion():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job.video_marked_for_deletion, 'interval', minutes=1)
    scheduler.start()
    
def start_video_marked_for_deletion():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job.video_marked_for_deletion, 'interval', minutes=1)
    scheduler.start()
    
def start_delete_video_search():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job.delete_video_search_records, 'interval', minutes=1)
    scheduler.start()

def start_delete_picture_query():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job.delete_picture_search_records, 'interval', minutes=1)
    scheduler.start()
    
def start_convert_temp_youtube_record():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job.convert_temp_youtube_record, 'interval', minutes=1)
    scheduler.start()

def start_create_music_record():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job.create_music_record, 'interval', minutes=1)
    scheduler.start()
    
def start_data_source_cleaning():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job.data_source_cleaning, 'interval', minutes=1)
    scheduler.start()
    
def start_create_graph_and_table_dashboard_items():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job.create_graph_and_table_dashboard_items, 'interval', minutes=1)
    scheduler.start()

def start_check_music_full_track():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job.check_music_full_track, 'interval', minutes=1)
    scheduler.start()
    
def start_parse_article_json_file():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job.parse_article_json_file, 'interval', minutes=1)
    scheduler.start()
    
def start_validate_scraper_links():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job.validate_scraper_links, 'interval', minutes=1)
    scheduler.start()

def start_run_scraper_jobs():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job.run_scraper_jobs, 'interval', minutes=1)
    scheduler.start()