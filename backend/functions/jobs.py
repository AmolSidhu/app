from moviepy.editor import VideoFileClip
from django.utils import timezone
from collections import defaultdict
from django.db.models import F
import numpy as np
import subprocess
import logging
import librosa
import json
import cv2
import os
import re
import av

from core.serializer import VideoSerializer, IdentifierSerializer, VideoRecordSerializer, FailedVideoRecordsSerializer
from videos.models import Video, TempVideo, VideoRecord, VideoGenre, VideoTags, VideoDirectors, VideoStars, VideoWriters, VideoCreators
from management.models import Identifier, IdentifierTempTable, TempGenreTable
from .scraper import imdb_scraper
from .json_formats import json_imdb_video_record

logger = logging.getLogger(__name__)

def check_corruption_temp():
    videos = TempVideo.objects.filter(corruption_check_temp=False,
                                       current_status="U")

    for video in videos:
        try:
            check = av.open(video.temp_video_location + video.serial + '.' + video.temp_video_extension)
            if not check or not check.streams.video:
                video.current_status = "C"
                video.last_updated = timezone.now()
                video.save()
                continue
            
            video.corruption_check_temp = True
            video.current_status = "B"
            video.last_updated = timezone.now()
            video.save()
            
        except Exception as e:
            logger.error(f"Error during initial corruption check for video {video.serial}: {str(e)}")
            
            if video.failed_attempts >= 3:
                video.failed_attempts += 1
                video.last_updated = timezone.now()
                video.current_status = "E"
            else:
                video.last_updated = timezone.now()
                video.failed_attempts += 1
            
            video.save()

def convert_video():
    with open('directory.json', 'r') as f:
        directory = json.load(f)
    
    video_location = directory['video_dir']
    os.makedirs(video_location, exist_ok=True)
    
    videos = TempVideo.objects.filter(format_conversion=False,
                                       current_status="B")
    
    for video in videos:
        try:
            output_path = os.path.join(video_location, f'{video.serial}.mp4')
            command = [
                'ffmpeg',
                '-hwaccel', 'cuda',
                '-i', f'{video.temp_video_location}{video.serial}.{video.temp_video_extension}',
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:v', '2M',
                '-vf', 'yadif',
                output_path
            ]
            
            subprocess.run(command)
            
            video.format_conversion = True
            video.current_status = "G"
            video.last_updated = timezone.now()
            video.video_location = video_location
            video.save()
            
        except Exception as e:
            logger.error(f"Error during video {video.serial} conversion: {str(e)}")
            
            if video.failed_attempts >= 3:
                video.failed_attempts += 1
                video.last_updated = timezone.now()
                video.current_status = "E"
            else:
                video.last_updated = timezone.now()
                video.failed_attempts += 1
            
            video.save()
    
def check_corruption_data():
    videos = TempVideo.objects.filter(corruption_check_data=False,
                                       current_status="G")
    for video in videos:
        try:
            check = av.open(f'{video.video_location}{video.serial}.mp4')
            if not check or not check.streams.video:
                video.current_status = "C"
                video.last_updated = timezone.now()
                video.save()
                continue
            
            video.corruption_check_data = True
            video.current_status = "H"
            video.last_updated = timezone.now()
            video.save()
            
        except Exception as e:
            logger.error(f"Error during corruption check for video {video.serial}: {str(e)}")
            
            if video.failed_attempts >= 3:
                video.failed_attempts += 1
                video.last_updated = timezone.now()
                video.current_status = "E"
            else:
                video.last_updated = timezone.now()
                video.failed_attempts += 1
            
            video.save()
    
def imdb_data():
    videos = TempVideo.objects.filter(imdb_added=False, current_status="H")
    
    for video in videos:
        try:
            existing_record = None
            if video.existing_series:
                existing_record = Video.objects.filter(
                    serial=video.master_serial
                ).first() or TempVideo.objects.filter(
                    master_serial=video.master_serial
                ).first()

            if video.imdb_link is None or video.imdb_link == '':
                if existing_record:
                    pass
                else:
                    video.current_status = "J"
                    video.imdb_added = True
                    video.last_updated = timezone.now()
                    video.save()
                    continue
                
            
            previous_passed_record = None
            if video.series == True and existing_record == None:
                previous_passed_record = TempVideo.objects.filter(
                    master_serial=video.master_serial,
                    imdb_added=True,
                    image_added=True
                ).exclude(
                    serial = video.serial
                ).first()
        
            if existing_record or previous_passed_record:
                video.current_status = "J"
                video.imdb_added = True
                video.image_added = True
                video.title = existing_record.title if existing_record else previous_passed_record.title
                video.description = existing_record.description if existing_record else previous_passed_record.description
                video.imdb_rating = existing_record.imdb_rating if existing_record else previous_passed_record.imdb_rating
                video.imdb_link = existing_record.imdb_link if existing_record else previous_passed_record.imdb_link
                video.main_tag = existing_record.main_tag if existing_record else previous_passed_record.main_tag
                if previous_passed_record and not existing_record:
                    video.directors = previous_passed_record.directors
                    video.writers = previous_passed_record.writers
                    video.stars = previous_passed_record.stars
                    video.creators = previous_passed_record.creators
                    video.tags = previous_passed_record.tags
                video.save()
                continue

            imdb_record = imdb_scraper(video.imdb_link, video.master_serial, identifier=False)

            video.title = imdb_record['title']
            video.description = imdb_record['description']
            video.tags = imdb_record['all_genres']
            video.imdb_rating = imdb_record['rating']
            video.main_tag = imdb_record['main_genre']
            video.image_added = imdb_record['thumbnail_added']
            video.directors = imdb_record['all_directors_limited']
            video.writers = imdb_record['all_writers_limited']
            video.stars = imdb_record['all_stars_limited']
            video.creators = imdb_record['all_creators_limited']
            video.thumbnail_location = imdb_record['thumbnail_location']
            video.imdb_added = True
            video.current_status = "J"
            video.age_rating = imdb_record['age_rating']
            video.last_updated = timezone.now()
            video.save()

        except Exception as e:
            if video.imdb_failed_attempts >= 3:
                video.current_status = "J"
                video.imdb_added = True
                video.last_updated = timezone.now()
                video.imdb_failed_attempts += 1
            else:
                video.imdb_failed_attempts += 1
                video.last_updated = timezone.now()    
            video.save()

def identifier_check():
    videos = TempVideo.objects.filter(imdb_added=True,
                                      current_status="J")
    
    with open('directory.json', 'r') as f:
        directory = json.load(f)
    
    for video in videos:
        try:
            imdb_id_regex = r't{1}t\d+'
            imdb_id = re.search(imdb_id_regex, video.imdb_link).group()
            
            existing_identifier = Identifier.objects.filter(identifier=imdb_id)
            if not existing_identifier.exists():
                identifier_record = Identifier.objects.create(
                    identifier=imdb_id,
                    current_status="N",
                    json_location=directory['json_records_dir']
                )
                serializer = IdentifierSerializer(identifier_record)
            
            video.current_status = "M"
            video.last_updated = timezone.now()
            video.identifier_checked = True
            video.save()
        except Exception as e:
            logger.error(f"Error during identifier check for video {video.serial}: {str(e)}")
            
            if video.failed_attempts >= 3:
                video.current_status = "E"
                video.last_updated = timezone.now()
                video.failed_attempts += 1
            else:
                video.failed_attempts += 1
                video.last_updated = timezone.now()
            
            video.save()
     
def audio_profile():   
    videos = TempVideo.objects.filter(identifier_checked=True,
                                       current_status="M")
    
    for video in videos:
        try:
            clip = VideoFileClip(f'{video.video_location}{video.serial}.mp4')
            audio_path = f'{video.video_location}{video.serial}.wav'
            clip.audio.write_audiofile(audio_path, codec='pcm_s16le')
            
            y, sr = librosa.load(audio_path, sr=None, mono=True)
            
            average_volume = np.mean(librosa.feature.rms(y=y))
            
            audio_profile = {
                'duration': clip.duration,
                'sample_rate': sr,
                'channels': y.shape[0],
                'average_volume': average_volume
            }
            
            audio_details = {key: float(value) if not isinstance(value, tuple) else value for key, value in audio_profile.items()}
            
            video.audio_details = audio_details
            video.audio_data_added = True
            video.current_status = "K"
            video.last_updated = timezone.now()
            video.save()
            
            os.remove(audio_path)
            
        except Exception as e:
            logger.error(f"Error during audio profile calculation for video {video.serial}: {str(e)}")
            
            if video.failed_attempts >= 3:
                video.failed_attempts += 1
                video.last_updated = timezone.now()
                video.current_status = "E"
            else:
                video.last_updated = timezone.now()
                video.failed_attempts += 1
            
            video.save()

def visual_profile():
    videos = TempVideo.objects.filter(visual_data_added=False, current_status="K")
    
    for video in videos:
        try:
            filename = video.master_serial
            
            video_path = f'{video.video_location}{video.serial}.mp4'
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.error(f"Failed to open video file {video_path}")
                continue
            
            with open('directory.json', 'r') as f:
                directory = json.load(f)
            
            thumbnail_location = directory['thumbnail_dir']
            
            total_saturation = 0
            frame_count = 0
            
            if not video.existing_series:
                thumbnail_path = f'{video.thumbnail_location}{filename}.jpg'
                
                if not os.path.exists(thumbnail_path) or video.imdb_link_failed or not video.image_added:
                    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                    target_frame = int(total_frames * 0.1)
                    
                    ret, frame = cap.read()
                    if not ret:
                        logger.error(f"Failed to read frame for {video.serial}")
                        continue
                    
                    cv2.imwrite(thumbnail_path, frame)
                    video.thumbnail_location = thumbnail_location
                    video.save()
                    
                    cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
            
            ret, frame = cap.read()
            if not ret:
                logger.error(f"Failed to read frame for saturation calculation for {video.serial}")
                continue
            
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            saturation = np.mean(hsv[:,:,1]) / 255.0
            total_saturation += saturation
            frame_count += 1
            
            average_saturation = total_saturation / frame_count if frame_count > 0 else 0
            
            visual_profile_data = {
                'duration': cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS) if cap.get(cv2.CAP_PROP_FPS) != 0 else 0,
                'resolution': (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))),
                'frame_rate': cap.get(cv2.CAP_PROP_FPS),
                'average_saturation': average_saturation
            }

            video.visual_profile = visual_profile_data
            video.visual_data_added = True
            video.current_status = "V"
            video.last_updated = timezone.now()
            video.save()
            
        except Exception as e:
            logger.error(f"Error during visual profile calculation for video {filename}: {str(e)}")
            
            if video.failed_attempts >= 3:
                video.current_status = "E"
                video.failed_attempts += 1
            else:
                video.failed_attempts += 1
            
            video.last_updated = timezone.now()
            video.save()

def completed_processing():
    videos = TempVideo.objects.filter(
        corruption_check_temp=True,
        format_conversion=True,
        corruption_check_data=True,
        imdb_added=True,
        image_added=True,
        visual_data_added=True,
        audio_data_added=True,
        upload_success=True,
        current_status="V"
    )
    
    for video in videos:
        try:
            skip_video_creation_instance = False
            existing_series_record = Video.objects.filter(serial=video.master_serial).first()
            
            if existing_series_record:
                existing_series_record.update_series = False
                existing_series_record.save()
                skip_video_creation_instance = True
                
            if not skip_video_creation_instance:
                video_instance = Video.objects.create(
                    serial=video.master_serial,
                    title=video.title,
                    series=video.series,
                    imdb_link=video.imdb_link,
                    imdb_rating=video.imdb_rating,
                    thumbnail_location=video.thumbnail_location,
                    main_tag=video.main_tag,
                    permission=video.permission,
                    private=video.private,
                    uploaded_by=video.uploaded_by,
                    uploaded_date=video.uploaded_date,
                    last_updated=video.last_updated,
                    description=video.description,
                    current_status="P",
                    update_series=False,
                )
                
                is_new_video_instance = True
            else:
                video_instance = existing_series_record
                is_new_video_instance = False
            
            if video_instance is None:
                raise Exception("Failed to create video instance")
            
            video_record_instance = VideoRecord.objects.create(
                master_record=video_instance,
                video_serial=video.serial,
                video_location=video.video_location,
                video_name=video.video_name,
                visual_profile=video.visual_profile,
                audio_profile=video.audio_details,
                visual_details=video.visual_details,
                audio_details=video.audio_details,
                series=video.series,
                season=video.season,
                episode=video.episode,
                current_status="P",
                last_updated=timezone.now(),
            )
            record = VideoRecordSerializer(video_record_instance)
        
            if is_new_video_instance:
                for tag in video.tags:
                    VideoTags.objects.create(
                        video=video_instance,
                        tag=tag
                    )
                for director in video.directors:
                    VideoDirectors.objects.create(
                        video=video_instance,
                        director=director
                    )
                for star in video.stars:
                    VideoStars.objects.create(
                        video=video_instance,
                        star=star
                    )
                for writer in video.writers:
                    VideoWriters.objects.create(
                        video=video_instance,
                        writer=writer
                    )
                for creator in video.creators:
                    VideoCreators.objects.create(
                        video=video_instance,
                        creator=creator
                    )
            
            os.remove(f'{video.temp_video_location}{video.serial}.{video.temp_video_extension}')
            video.delete()

        except Exception as e:
            logger.error(f"Error during video record creation for {video.serial}: {str(e)}")
            if video.failed_attempts >= 3:
                video.current_status = "E"
                video.last_updated = timezone.now()
                video.failed_attempts += 1
            
            else:
                video.failed_attempts += 1
                video.last_updated = timezone.now()
            
            video.save()
  

def failed_or_error_processing():
    failed_processing = TempVideo.objects.filter(current_status="E")
    
    for video in failed_processing:
        try:
            failed_record = FailedVideoRecordsSerializer(data={
                'serial': video.serial,
                'name': video.video_name,
                'title': video.title,
                'series': video.series,
                'season': video.season,
                'episode': video.episode,
                'imdb_link': video.imdb_link,
                'imdb_rating': video.imdb_rating,
                'main_tag': video.main_tag,
                'age_rating': video.age_rating,
                'tags': video.tags,
                'directors': video.directors,
                'stars': video.stars,
                'writers': video.writers,
                'creators': video.creators,
                'permission': video.permission,
                'private': video.private,
                'uploaded_by': video.uploaded_by,
                'uploaded_date': video.uploaded_date,
                'last_updated': timezone.now(),
                'description': video.description,
                'failed_attempts': video.failed_attempts,
                'temp_video_location': video.temp_video_location,
                'temp_video_extension': video.temp_video_extension,
                'video_location': video.video_location,
                'thumbnail_location': video.thumbnail_location,
                'audio_details': video.audio_details,
                'visual_profile': video.visual_profile,
                'visual_details': video.visual_details,
                'upload_success': video.upload_success,
                'imdb_added': video.imdb_added,
                'image_added': video.image_added,
                'audio_data_added': video.audio_data_added,
                'visual_data_added': video.visual_data_added,
                'corruption_check_temp': video.corruption_check_temp,
                'format_conversion': video.format_conversion,
                'corruption_check_data': video.corruption_check_data,
                'current_status': "E"
            })
            
            if failed_record.is_valid():
                failed_record.save()
                video.delete()
            else:
                logger.error(f"Failed to save failed video record for {video.serial}")
                video.delete()
            
        except Exception as e:
            logger.error(f"Error during failed video record creation for {video.serial}: {str(e)}")
            video.delete()
    
    corrupted_processing = TempVideo.objects.filter(current_status="C")
    
    for video in corrupted_processing:
        try:
            failed_record = FailedVideoRecordsSerializer(data={
                'serial': video.serial,
                'name': video.video_name,
                'title': video.title,
                'series': video.series,
                'season': video.season,
                'episode': video.episode,
                'imdb_link': video.imdb_link,
                'imdb_rating': video.imdb_rating,
                'main_tag': video.main_tag,
                'age_rating': video.age_rating,
                'tags': video.tags,
                'directors': video.directors,
                'stars': video.stars,
                'writers': video.writers,
                'creators': video.creators,
                'permission': video.permission,
                'private': video.private,
                'uploaded_by': video.uploaded_by,
                'uploaded_date': video.uploaded_date,
                'last_updated': timezone.now(),
                'description': video.description,
                'failed_attempts': video.failed_attempts,
                'temp_video_location': video.temp_video_location,
                'temp_video_extension': video.temp_video_extension,
                'video_location': video.video_location,
                'thumbnail_location': video.thumbnail_location,
                'audio_details': video.audio_details,
                'visual_profile': video.visual_profile,
                'visual_details': video.visual_details,
                'upload_success': video.upload_success,
                'imdb_added': video.imdb_added,
                'image_added': video.image_added,
                'audio_data_added': video.audio_data_added,
                'visual_data_added': video.visual_data_added,
                'corruption_check_temp': video.corruption_check_temp,
                'format_conversion': video.format_conversion,
                'corruption_check_data': video.corruption_check_data,
                'current_status': "C"
            })
            
            if failed_record.is_valid():
                failed_record.save()
                video.delete()
            else:
                logger.error(f"Failed to save corrupted video record for {video.serial}")
                video.delete()
            
        except Exception as e:
            logger.error(f"Error during corrupted video record creation for {video.serial}: {str(e)}")
            video.delete()
            
def add_identifiers():
    temp_data = IdentifierTempTable.objects.all()
    
    with open('directory.json', 'r') as f:
        directory = json.load(f)
    
    for data in temp_data:
        file_path = data.file_location + data.temp_name + '.json'
        with open(file_path, 'r') as f:
            entries = json.load(f)
            for entry in entries:
                try:
                    existing_identifier = Identifier.objects.filter(
                        identifier=entry).first()
                    if existing_identifier is None:
                        identify_record = Identifier.objects.create(
                            identifier=entry,
                            current_status="S",
                            json_location=directory['json_records_dir']
                        )
                        serializer = IdentifierSerializer(identify_record)
                except Exception as e:
                    print(e)
                    pass
            f.close()
            os.remove(file_path)
            data.delete()

def create_json_record():
    identifiers = Identifier.objects.filter(current_status="N")[:10]
    
    for identifier in identifiers:
        try:
            imdb_link = f'https://www.imdb.com/title/{identifier.identifier}/'
            serial = ''
            identifier_record = imdb_scraper(imdb_link, serial, identifier=True)
            
            json_file = json_imdb_video_record(
                title = identifier_record['title'],
                release_year=identifier_record['release_year'],
                full_release_date=identifier_record['full_release_date'],
                motion_picture_rating=identifier_record['age_rating'],
                tv_series=identifier_record['is_tv_series'],
                runtime=identifier_record['runtime_duration'],
                description=identifier_record['description'],
                main_genre=identifier_record['main_genre'],
                all_genres=identifier_record['all_genres'],
                interests=identifier_record['all_interests'],
                rating=identifier_record['rating'],
                popularity=identifier_record['popularity'],
                thumbnail_url=identifier_record['thumbnail_url'],
                full_image_url=identifier_record['full_image_url'],
                directors=identifier_record['all_directors'],
                creators=identifier_record['all_creators'],
                stars=identifier_record['all_stars'],
                writers=identifier_record['all_writers']
            )
            
            with open('directory.json', 'r') as f:
                directory = json.load(f)
                
            json_records_dir = directory['json_records_dir']
            os.makedirs(json_records_dir, exist_ok=True)
            
            with open (f'{json_records_dir}{identifier.identifier}.json',
                    'w', encoding='utf-8') as f:
                json.dump(json_file, f, indent=4, ensure_ascii=False)
                f.close()
                
            identifier.current_status = "R"
            identifier.title = identifier_record['title']
            identifier.json_location = json_records_dir
            identifier.last_updated = timezone.now()
            identifier.save()
        except Exception as e:
            logger.error(f"Error during JSON record creation for {identifier.identifier}: {str(e)}")
            identifier.delete()

def check_existing_genres():
    TempGenreTable.objects.all().delete()
    VideoTags.objects.filter(tag_updated=True).update(tag_updated=False)

    known_genres = ['Action', 'Adventure', 'Animation', 'Biography', 'Comedy',
                    'Crime', 'Documentary', 'Drama', 'Family', 'Fantasy',
                    'Film-Noir', 'History', 'Horror', 'Music', 'Musical',
                    'Mystery', 'Romance', 'Sci-Fi', 'Sport', 'Thriller',
                    'War', 'Western']

    finished = False
    while not finished:
        video_record = VideoTags.objects.filter(tag_updated=False).first()
        if video_record is None:
            finished = True
            break

        tags = video_record.tag
        if isinstance(tags, str):
            tags = [tags]

        for tag in tags:
            existing_record = TempGenreTable.objects.filter(genre=tag).first()
            if existing_record:
                existing_record.number_of_public_records += 1
                existing_record.save()
            else:
                custom = tag not in known_genres
                TempGenreTable.objects.create(
                    genre=tag,
                    number_of_public_records=1,
                    custom=custom
                )

        video_record.tag_updated = True
        video_record.save()

    VideoGenre.objects.all().delete()
    temp_data = TempGenreTable.objects.all()
    for data in temp_data:
        VideoGenre.objects.create(
            genre=data.genre,
            number_of_public_records=data.number_of_public_records,
            custom=data.custom
        )
        data.delete()

def check_series_data():
    finished = False
    
    while not finished:
        video_record = Video.objects.filter(current_status='P',
                                            update_series=False,
                                            series=True).first()
        if video_record is None:
            finished = True
            break
        
        series_videos = VideoRecord.objects.filter(master_record=video_record,
                                                   current_status='P')
        
        if not series_videos.exists():
            video_record.update_series = True
            video_record.save()
            continue
        
        seasons = defaultdict(int)
        for sv in series_videos:
            seasons[sv.season] += 1
        
        video_record.total_seasons = len(seasons)
        video_record.total_episodes = sum(seasons.values())
        video_record.season_metadata = {str(season): count for season, count in seasons.items()}
        video_record.update_series = True
        video_record.save()

def video_marked_for_deletion():
    return None

def delete_video_search_records():
    return None

def delete_picture_search_records():
    return None