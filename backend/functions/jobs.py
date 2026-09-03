from moviepy.editor import VideoFileClip
from django.utils import timezone
from collections import defaultdict
from secrets import token_urlsafe
from PIL import Image
from decimal import Decimal

import numpy as np
import pandas as pd
import subprocess
import logging
import shutil
import librosa
import uuid
import json
import cv2
import os
import re
import av

from core.serializer import (IdentifierSerializer,
                             VideoRecordSerializer, FailedVideoRecordsSerializer)
from videos.models import (Video, TempVideo, VideoRecord, VideoGenre, VideoTags,
                           VideoDirectors, VideoStars, VideoWriters, VideoCreators,
                           VideoQuery, VideoFavourites, VideoRating,
                           VideoHistory, VideoComments, CustomVideoListRecords)
from management.models import Identifier, IdentifierTempTable, TempGenreTable
from youtube.models import YoutubeTempRecord, YoutubeVideoRecord, YoutubeListRecord, YoutubeLists, YoutubeVideoMetadata
from music.models import (MusicTempRecord, ArtistRecord, ArtistGenres, MusicAlbumRecord, MusicTrackRecord,
                          MusicFullTrackRecord, AddedFullTrackTemp)
from analytics.models import DataSourceUpload, Dashboards, DashboardItem, DashboardTableDataLines, DashboardGraphData
from mtg.models import (ScraperUploadFile, ScraperOutputFile, MagicCards, MagicTempFiles, MagicCardsView,
                        MagicCardLegalities, MagicCardPrices, MagicCardKeywords, MagicCardUris, MagicCardMiscData,
                        CompletedTempFilesLog)
from pictures.models import PictureQuery
from admins.models import AdminFileRecord
from .job_functions.scraper import imdb_scraper
from .job_functions.youtube_download_function import process_youtube_video
from .json_formats import json_imdb_video_record, json_music_artist_record, json_music_album_record
from .job_functions.music_api import get_spotify_music_data, get_apple_music_data
from .job_functions.create_graphs import generate_basic_graph
from .job_functions.create_table import create_table
from .check_functions.serial_default_generator import generate_serial_code
from .job_functions.mtg_f2f_scraper import mtg_f2f_scraper
from .job_functions.youtube_mp3_downloader import youtube_mp3_downloader
from .job_functions.music_track_check import compare_tracks
from .job_functions.admin_file_verification import chunk_magic_data_file
from .job_functions.create_mtg_records import magic_image_downloader
from .job_functions.mtg_data_sorters import legalities_sorter, prices_sorter, magic_color_identifier

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
    with open('json/directory.json', 'r') as f:
        directory = json.load(f)
    video_location = directory['video_transition_dir']
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
                    serial=video.existing_series_serial
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
            print(f"Processing IMDb data for video {video.serial}")
            print(f"IMDb Link: {video.master_serial}")

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
            logger.error(f"Error during IMDb data processing for video {video.serial}: {str(e)}")
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
    videos = TempVideo.objects.filter(imdb_added=True, current_status="J")

    with open('json/directory.json', 'r') as f:
        directory = json.load(f)

    for video in videos:
        try:
            if not video.existing_series:
                imdb_id_regex = r't{1}t\d+'
                imdb_id = re.search(imdb_id_regex, video.imdb_link).group()

                existing_identifier = Identifier.objects.filter(identifier=imdb_id)
                if not existing_identifier.exists():
                    identifier_record = Identifier.objects.create(
                        identifier=imdb_id,
                        current_status="N",
                        json_location=directory['json_imdb_records_dir']
                    )
                    serializer = IdentifierSerializer(identifier_record)

            video.current_status = "M"
            video.last_updated = timezone.now()
            video.identifier_checked = True
            video.save()

        except Exception as e:
            logger.error(f"Error during identifier check for video {video.serial}: {str(e)}")

            video.failed_attempts += 1
            video.last_updated = timezone.now()
            if video.failed_attempts >= 3:
                video.current_status = "E"

            video.save()

     
def audio_profile():   
    videos = TempVideo.objects.filter(identifier_checked=True, current_status="M")
    
    for video in videos:
        clip = None
        try:
            video_path = os.path.join(video.video_location, f"{video.serial}.mp4")
            audio_path = os.path.join(video.video_location, f"{video.serial}.wav")

            clip = VideoFileClip(video_path)
            clip.audio.write_audiofile(audio_path, codec='pcm_s16le')

            y, sr = librosa.load(audio_path, sr=None, mono=True)
            average_volume = float(np.mean(librosa.feature.rms(y=y)))

            audio_profile = {
                'duration': clip.duration,
                'sample_rate': sr,
                'channels': 1 if y.ndim == 1 else y.shape[0],
                'average_volume': average_volume
            }

            video.audio_details = audio_profile
            video.audio_data_added = True
            video.current_status = "K"
            video.last_updated = timezone.now()
            video.save()

        except Exception as e:
            logger.error(f"Error during audio profile calculation for video {video.serial}: {str(e)}")
            video.failed_attempts += 1
            if video.failed_attempts >= 3:
                video.current_status = "E"
            video.last_updated = timezone.now()
            video.save()

        finally:
            if clip:
                clip.close()
            if os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                except PermissionError:
                    logger.warning(f"Could not remove {audio_path}, file still in use.")


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
            
            with open('json/directory.json', 'r') as f:
                directory = json.load(f)
            
            thumbnail_location = directory['video_thumbnail_dir']
            
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
                'duration': cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(
                    cv2.CAP_PROP_FPS) if cap.get(cv2.CAP_PROP_FPS) != 0 else 0,
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
            
        finally:
            cap.release()

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

            with open('json/directory.json', 'r') as f:
                directory = json.load(f)
            
            if not existing_series_record:
 
                video_serial = generate_serial_code(
                    config_section="videos",
                    serial_key="video_serial_code",
                    model=Video,
                    field_name="serial"
                )

            video_record_serial = generate_serial_code(
                config_section="videos",
                serial_key="video_record_serial_code",
                model=VideoRecord,
                field_name="video_serial"
            )

            if existing_series_record:
                existing_series_record.update_series = False
                existing_series_record.save()
                skip_video_creation_instance = True
                
            if not existing_series_record and video.series:
                all_additional_series_records = TempVideo.objects.filter(
                    master_serial=video.master_serial,
                ).exclude(
                    serial=video.serial
                )
                for additional_series in all_additional_series_records:
                    additional_series.existing_series = True
                    additional_series.existing_series_serial = video_serial
                    additional_series.save()

            if not skip_video_creation_instance:
                thumbnail_dir = directory['video_thumbnail_dir']
                os.makedirs(thumbnail_dir, exist_ok=True)

                full_thumbnail_path = thumbnail_dir + video_serial + '.jpg'
                original_thumbnail_path = video.thumbnail_location + video.master_serial + '.jpg'

                if os.path.exists(original_thumbnail_path):
                    shutil.move(original_thumbnail_path, full_thumbnail_path)
                else:
                    existing_thumbnail_path = thumbnail_dir + video.existing_series_serial + '.jpg'
                    if not os.path.exists(existing_thumbnail_path):
                        raise FileNotFoundError(f"Thumbnail file not found: {existing_thumbnail_path}")

                video_instance = Video.objects.create(
                    serial=video_serial,
                    title=video.title,
                    series=video.series,
                    imdb_link=video.imdb_link,
                    imdb_rating=video.imdb_rating,
                    thumbnail_location=thumbnail_dir,
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
                video_instance.save()
            else:
                video_instance = existing_series_record
                is_new_video_instance = False

            if video_instance is None:
                raise Exception("Failed to create or retrieve video instance.")

            master_serial = Video.objects.get(serial=video.master_serial) if video.existing_series else video_instance

            video_dir = directory['video_dir']
            os.makedirs(video_dir, exist_ok=True)

            full_video_path = video_dir + video_record_serial + '.mp4'
            original_video_path = video.video_location + video.serial + '.mp4'

            logger.info(f"Moving video: {original_video_path} → {full_video_path}")
            if os.path.exists(original_video_path):
                shutil.move(original_video_path, full_video_path)
            else:
                raise FileNotFoundError(f"Video file not found: {original_video_path}")

            video_record_instance = VideoRecord.objects.create(
                master_record=master_serial,
                video_serial=video_record_serial,
                video_location=video_dir,
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
                    VideoTags.objects.create(video=video_instance, tag=tag)
                for director in video.directors:
                    VideoDirectors.objects.create(video=video_instance, director=director)
                for star in video.stars:
                    VideoStars.objects.create(video=video_instance, star=star)
                for writer in video.writers:
                    VideoWriters.objects.create(video=video_instance, writer=writer)
                for creator in video.creators:
                    VideoCreators.objects.create(video=video_instance, creator=creator)

            temp_video_path = f'{video.temp_video_location}{video.serial}.{video.temp_video_extension}'
            logger.info(f"Deleting temp video: {temp_video_path}")
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)
            else:
                logger.warning(f"Temp video file not found for deletion: {temp_video_path}")

            video.delete()

        except Exception as e:
            logger.error(f"Error during video record creation for {video.serial}: {str(e)}")

            video.failed_attempts += 1
            video.last_updated = timezone.now()

            if video.failed_attempts >= 3:
                video.current_status = "E"

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
    
    with open('json/directory.json', 'r') as f:
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
                            json_location=directory['json_imdb_records_dir']
                        )
                        serializer = IdentifierSerializer(identify_record)
                except Exception as e:
                    logger.error(f"Error adding identifier {entry}: {str(e)}")
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
            
            with open('json/directory.json', 'r') as f:
                directory = json.load(f)
                
            json_records_dir = directory['json_imdb_records_dir']
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
        video_record.season_metadata = {str(season): count for season,
                                        count in seasons.items()}
        video_record.update_series = True
        video_record.save()

def video_marked_for_deletion():
    finished = False
    
    while not finished:
        try:
            video_to_delete = Video.objects.filter(current_status='D').first()
            if video_to_delete is None:
                finished = True
                break
            VideoFavourites.objects.filter(video=video_to_delete).delete()
            VideoRating.objects.filter(master_record=video_to_delete).delete()
            VideoHistory.objects.filter(master_record=video_to_delete).delete()
            VideoComments.objects.filter(master_record=video_to_delete).delete()
            VideoCreators.objects.filter(video=video_to_delete).delete()
            VideoWriters.objects.filter(video=video_to_delete).delete()
            VideoStars.objects.filter(video=video_to_delete).delete()
            VideoDirectors.objects.filter(video=video_to_delete).delete()
            VideoTags.objects.filter(video=video_to_delete).delete()
            CustomVideoListRecords.objects.filter(video_serial=video_to_delete).delete()
            VideoRecord.objects.filter(master_record=video_to_delete).delete()
            video_to_delete.delete()
        except:
            pass
    return None

def delete_video_search_records():
    pass
    current_time = timezone.now()
    VideoQuery.objects.filter(query_date__lt=current_time - timezone.timedelta(
        days=30)).delete()
    return None

def delete_picture_search_records():
    pass
    current_time = timezone.now()
    PictureQuery.objects.filter(query_date__lt=current_time - timezone.timedelta(
        days=30)).delete()
    return None

def convert_temp_youtube_record():
    finished = False

    while not finished:

        temp_record = YoutubeTempRecord.objects.filter(failed_status=False).first()
        if not temp_record:
            finished = True
            break

        try:
            serial = generate_serial_code(
                config_section="youtube",
                serial_key="youtube_video_record_serial_code",
                model=YoutubeVideoRecord,
                field_name="serial"
            )

            youtube_data = process_youtube_video(
                video_url=temp_record.youtube_link,
                video_output_dir=temp_record.youtube_video_location,
                thumbnail_output_dir=temp_record.youtube_thumbnail_location,
                serial=serial,
            )

            if youtube_data is None:
                logger.error(f"Failed processing YouTube video for {temp_record.serial}")
                temp_record.failed_status = True
                temp_record.save()
                continue

            new_record = YoutubeVideoRecord.objects.create(
                serial=serial,
                title=youtube_data["title"],
                description=youtube_data["description"],
                thumbnail_path=temp_record.youtube_thumbnail_location,
                video_path=temp_record.youtube_video_location,
                update_date=timezone.now(),
                user=temp_record.user,
            )

            playlist_serials = [s.strip() for s in temp_record.add_to_playlists]
            playlists = YoutubeLists.objects.filter(serial__in=playlist_serials)
            all_playlists = {p.serial: p for p in playlists}

            for serial in playlist_serials:
                playlist = all_playlists.get(serial)
                if not playlist:
                    logger.warning(f"Playlist not found: {serial}")
                    continue

                record_serial = generate_serial_code(
                    config_section="youtube",
                    serial_key="youtube_list_record_serial_code",
                    model=YoutubeListRecord,
                    field_name="serial"
                )

                list_record = YoutubeListRecord.objects.create(
                    serial=record_serial,
                    youtube_list=playlist,
                    youtube_video=new_record,
                )
                list_record.save()
                
                metadata_record = YoutubeVideoMetadata.objects.create(
                    youtube_video = new_record,
                    video_id = youtube_data["video_id"],
                    full_title = youtube_data["title"],
                    alt_title = youtube_data["alt_title"],
                    uploader = youtube_data["uploader"],
                    uploader_id = youtube_data["uploader_id"],
                    uploader_url = youtube_data["uploader_url"],
                    video_license = youtube_data["video_license"],
                    creators = youtube_data["creators"],
                    upload_time = youtube_data["upload_time"],
                    upload_date = youtube_data["upload_date"],
                    release_time = youtube_data["release_time"],
                    release_date = youtube_data["release_date"],
                    modified_timestamp = youtube_data["modified_timestamp"],
                    modified_date = youtube_data["modified_date"],
                    channel = youtube_data["channel"],
                    channel_id = youtube_data["channel_id"],
                    channel_url = youtube_data["channel_url"],
                    duration = youtube_data["duration"],
                    duration_formatted = youtube_data["duration_formatted"],
                    age_limit = youtube_data["age_limit"],
                    media_type = youtube_data["media_type"],
                    tags = youtube_data["tags"],
                    categories = youtube_data["categories"],
                )
                
                metadata_record.save()

            temp_record.delete()

        except Exception as e:
            logger.error(f"Error during YouTube video processing for {temp_record.serial}: {str(e)}")
            temp_record.failed_status = True
            temp_record.save()

            video_path = os.path.join(temp_record.youtube_video_location,
                                      f"{temp_record.serial}.mp4")
            thumbnail_path = os.path.join(temp_record.youtube_thumbnail_location,
                                          f"{temp_record.serial}.jpg")
            if os.path.exists(video_path):
                os.remove(video_path)
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
            continue

def create_music_record():
    finished = False
    while not finished:
        music_record = MusicTempRecord.objects.filter(failed_status=False).first()
        if music_record is None:
            finished = True
            break

        spotify_data = get_spotify_music_data(spotify_link=music_record.spotify_link)
        if not spotify_data:
            logger.error(f"Failed to fetch Spotify data for: {music_record.spotify_link}")
            music_record.failed_status = True
            music_record.save()
            continue

        album_info = spotify_data['album_info']
        artist_info_list = spotify_data['artist_info']
        if not artist_info_list:
            logger.error(f"No artist info found for: {music_record.spotify_link}")
            music_record.failed_status = True
            music_record.save()
            continue
        artist_info = artist_info_list[0]

        track_ids = [track['track_id'] for track in album_info['tracks']]

        with open('json/directory.json', 'r') as f:
            directory = json.load(f)
        apple_music_path = directory['music_track_preview_dir']

        apple_data = get_apple_music_data(
            apple_link=music_record.apple_link,
            tracks=track_ids,
            apple_music_path=apple_music_path
        )

        try:
            existing_record= None
            artist_record_instance = ArtistRecord.objects.filter(serial=artist_info['artist_id']).first()

            if not artist_record_instance:
                new_artist_record = ArtistRecord.objects.create(
                    serial=artist_info['artist_id'],
                    user=music_record.user,
                    artist_name=artist_info['artist_name'],
                    artist_image_location=artist_info['artist_image_location'],
                    artist_popularity=artist_info['popularity'],
                    artist_followers=artist_info['followers'],
                    artist_spotify_link=artist_info['spotify_url'],
                )
                new_artist_record.save()

                artist_record_instance = ArtistRecord.objects.filter(serial=artist_info['artist_id']).first()

                json_artist_record = json_music_artist_record(
                    artist_name=artist_info['artist_name'],
                    artist_id=artist_info['artist_id'],
                    popularity=artist_info['popularity'],
                    followers=artist_info['followers'],
                    spotify_url=artist_info['spotify_url'],
                    genres=artist_info['genres'],
                    image_url=artist_info['images'][0] if artist_info['images'] else None,
                )
                json_artist_dir = directory['music_artist_json_dir']
                os.makedirs(json_artist_dir, exist_ok=True)
                with open(f'{json_artist_dir}{artist_info["artist_id"]}.json',
                          'w', encoding='utf-8') as f:
                    json.dump(json_artist_record, f, indent=4, ensure_ascii=False)
                existing_record = False
            else:
                existing_record = True

            if artist_record_instance is not None:
                if existing_record is True:
                    pass
                else:
                    for genre in artist_info.get('genres', []):
                        genre_record = ArtistGenres.objects.create(
                            serial=token_urlsafe(16),
                            artist=artist_record_instance,
                            genre=genre,
                        )
                        genre_record.save()

                new_album_record = MusicAlbumRecord.objects.create(
                    serial=album_info['album_id'],
                    user=music_record.user,
                    artist_record=artist_record_instance,
                    album_name=album_info['album_name'],
                    album_image_location=album_info['album_image_location'],
                    album_popularity=album_info['popularity'],
                    album_type=album_info['album_type'],
                    release_date=album_info['release_date'],
                    total_tracks=album_info['total_tracks'],
                    album_spotify_link=album_info['album_spotify_url'],
                )
                new_album_record.save()

                json_album_record = json_music_album_record(
                    album_name=album_info['album_name'],
                    album_id=album_info['album_id'],
                    artist_id=artist_info['artist_id'],
                    album_type=album_info['album_type'],
                    release_date=album_info['release_date'],
                    total_tracks=album_info['total_tracks'],
                    album_spotify_link=album_info['album_spotify_url'],
                    album_popularity=album_info['popularity'],
                    album_image_location=album_info['images'],
                )
                json_album_dir = directory['music_album_json_dir']
                os.makedirs(json_album_dir, exist_ok=True)
                with open(f'{json_album_dir}{album_info["album_id"]}.json',
                          'w', encoding='utf-8') as f:
                    json.dump(json_album_record, f, indent=4, ensure_ascii=False)

                for track in album_info['tracks']:
                    new_music_track_record = MusicTrackRecord.objects.create(
                        serial=track['track_id'],
                        user=music_record.user,
                        album_record=new_album_record,
                        artist_record=artist_record_instance,
                        track_name=track['track_name'],
                        track_number=track['track_number'],
                        track_duration=track['duration_ms'],
                        track_location=apple_music_path
                    )
                    new_music_track_record.save()

                music_record.delete()
            else:
                logger.error(f"Artist record instance is None for artist_id: {artist_info['artist_id']}")

        except Exception as e:
            logger.error(f"Error during music record creation for {music_record.serial}: {str(e)}")
            music_record.failed_status = True
            music_record.save()

def data_source_cleaning():
    finished = False
    while not finished:
        data_source = DataSourceUpload.objects.filter(
            data_cleaning_status='pending').first()
        
        if data_source is None:
            finished = True
            break
        
        try:
            column_cleaning_methods = data_source.data_cleaning_method_for_columns
            row_cleaning_method = data_source.data_cleaning_method_for_rows
            override_column_cleaning = data_source.override_column_cleaning
            
            file = None
            
            try:
                file = data_source.edited_file_location + data_source.serial + '.csv'
            except Exception as e:
                pass
            
            if not data_source.edited_file_location:
                with open('json/directory.json', 'r') as f:
                    directory = json.load(f)
                data_source.edited_file_location = directory['data_source_cleaned_dir']
                data_source.save()
                
                file = data_source.file_location + data_source.serial + '.csv'
                
                raw_file = data_source.raw_file_location + data_source.serial + '.csv'
                os.makedirs(data_source.edited_file_location, exist_ok=True)
                shutil.copy(raw_file, file)
            
            df = pd.read_csv(file)
            
            total_cleaning_methods = len(column_cleaning_methods)
            total_columns = len(data_source.column_names)
            
            if total_cleaning_methods != total_columns:
                data_source.override_column_cleaning = True
                data_source.data_cleaning_method_for_rows = 'dropna'
                data_source.save()
                
            if override_column_cleaning is True:
                if row_cleaning_method == 'dropna':
                    df = df.dropna()
                if row_cleaning_method == 'dropna_with_threshold':
                    threshold = data_source.data_cleaning_row_cleaning_value
                    if threshold is None or threshold < 0:
                        logger.error(f"Invalid threshold value for data source {data_source.serial}: {threshold}")
                        data_source.data_cleaning_status = 'failed'
                        data_source.save()
                        continue
                    df = df.dropna(thresh=threshold)
                if row_cleaning_method == 'fillna_with_value':
                    value = data_source.data_cleaning_row_cleaning_value
                    if value is None:
                        logger.error(f"Invalid fill value for data source {data_source.serial}: {value}")
                        data_source.data_cleaning_status = 'failed'
                        data_source.save()
                        continue
                    df = df.fillna(value)
                if row_cleaning_method == 'interpolate':
                    df = df.interpolate()

            if override_column_cleaning is False:
                for column in column_cleaning_methods:
                    method = column_cleaning_methods[column]
                    if method == 'drop_duplicates':
                        df = df.drop_duplicates(subset=column)
                    if method == 'fillna_with_mean':
                        mean_value = df[column].mean()
                        df[column] = df[column].fillna(mean_value)
                    if method == 'fillna_with_median':
                        median_value = df[column].median()
                        df[column] = df[column].fillna(median_value)
                    if method == 'fillna_with_mode':
                        mode_value = df[column].mode()
                        if not mode_value.empty:
                            df[column] = df[column].fillna(mode_value[0])
                            
            full_path = data_source.edited_file_location + data_source.serial + '.csv'

            df.to_csv(full_path, index=True)
            data_source.data_cleaning_status = 'cleaned'
            data_source.save()

        except Exception as e:
            logger.error(f"Error during data source cleaning for {data_source.serial}: {str(e)}")
            data_source.data_cleaning_status = 'failed'
            data_source.save()

def create_graph_and_table_dashboard_items():
    finished = False
    while not finished:
        
        table_record = DashboardItem.objects.filter(
            data_item_created=False,
            data_item_failed_creation=False
        ).first()
        
        if table_record is None:
            finished = True
            break

        try:
            dashboard = Dashboards.objects.filter(
                dashboard_serial=table_record.dashboard.dashboard_serial,
                user=table_record.user
            ).first()
            
            data_source = DataSourceUpload.objects.filter(
                serial=dashboard.data_source.serial,
                user=table_record.user
            ).first()
                
            
            if table_record.data_item_type == 'Graph':
                
                graph_settings = DashboardGraphData.objects.filter(
                    dashboard_item_serial=table_record.dashboard_item_serial,
                    user=table_record.user
                ).first()
                
                graph = generate_basic_graph(
                    data_location=data_source.file_location,
                    serial=table_record.dashboard_item_serial,
                    graph_type=graph_settings.graph_type,
                    column_1=graph_settings.x_column,
                    column_2=graph_settings.y_column,
                    save_path=table_record.graph_location,
                    graph_title=graph_settings.graph_title,
                    x_label=graph_settings.x_axis_title,
                    y_label=graph_settings.y_axis_title,
                    columns=[graph_settings.x_column, graph_settings.y_column],
                    cleaning_method=graph_settings.cleaning_method,
                    data_source_serial=data_source.serial
                )
                
                if graph is True:
                    table_record.data_item_created = True
                    table_record.data_item_failed_creation = False
                    table_record.save()
                    continue
                
                else:
                    table_record.data_item_created = False
                    table_record.data_item_failed_creation = True
                    table_record.save()
                    continue
            
            if table_record.data_item_type == 'Table':
                table_items = DashboardTableDataLines.objects.filter(
                    dashboard_item_serial=table_record.dashboard_item_serial,
                    user=table_record.user
                )
                
                column_1 = []
                column_2 = []
                operation = []
                column_names = []
                if table_items.exists():
                    for item in table_items:
                        column_1.append(item.source_1)
                        column_2.append(item.source_2)
                        operation.append(item.operation)
                        column_names.append(item.column_name)
                table = create_table(
                    data_location=data_source.file_location,
                    serial=table_record.dashboard_item_serial,
                    data_source_serial=data_source.serial,
                    source_1_columns=column_1,
                    source_2_columns=column_2,
                    operations=operation,
                    save_path=table_record.table_location,
                    column_names=column_names,
                    data_sample_path=table_record.table_truncated_location
                )
                
                if table is True:
                    table_record.data_item_created = True
                    table_record.data_item_failed_creation = False
                    table_record.save()
                    continue

            else:
                table_record.data_item_created = False
                table_record.data_item_failed_creation = True
                table_record.save()
                continue

        except Exception as e:
            logger.error(f"Error during dashboard graph and table creation for {table_record.dashboard_item_serial}: {str(e)}")
            table_record.data_item_failed_creation = True
            table_record.save()
            continue
        
def convert_youtube_to_mp3():
    pass
    finished = False
    while not finished:
        temp_record = AddedFullTrackTemp.objects.filter(mp3_file_added=False,
                                                        record_status='pending').first()
        if temp_record is None:
            finished = True
            break
        try:
            run_conversion = youtube_mp3_downloader(
                url=temp_record.youtube_link,
                output_folder=temp_record.file_path,
                serial=temp_record.serial,
            )
            
            temp_record.mp3_file_added = True
            temp_record.save()
            
        except Exception as e:
            logger.error(f"Error during YouTube to MP3 conversion for {temp_record.serial}: {str(e)}")
            temp_record.record_status = 'failed'
            temp_record.save()
            continue

def create_youtube_track_record():
    finished = False
    while not finished:
        temp_record = AddedFullTrackTemp.objects.filter(
            mp3_file_added=True,
            record_status='completed'
        ).first()

        if temp_record is None:
            finished = True
            break

        try:
            track_record = MusicTrackRecord.objects.filter(
                serial=temp_record.track.serial
            ).first()

            album_record = MusicAlbumRecord.objects.filter(
                serial=track_record.album_record.serial
            ).first()

            full_track_exists = MusicFullTrackRecord.objects.filter(
                track=track_record
            ).exists()

            if full_track_exists:
                temp_record.record_status = 'failed'
                temp_record.save()
                continue

            with open('json/directory.json', 'r') as f:
                directory = json.load(f)

            full_track_dir = directory['music_full_track_dir']
            os.makedirs(full_track_dir, exist_ok=True)

            current_track_location = os.path.join(
                temp_record.file_path,
                f"{temp_record.serial}.mp3"
            )

            serial = generate_serial_code(
                config_section="music",
                serial_key="full_track_record_serial_code",
                model=MusicFullTrackRecord,
                field_name="serial"
            )

            shutil.move(
                current_track_location,
                os.path.join(full_track_dir, f"{serial}.mp3")
            )

            new_full_track_record = MusicFullTrackRecord.objects.create(
                serial=serial,
                album=album_record,
                track=track_record,
                track_location=full_track_dir,
            )

            track_record.full_track_added = True
            track_record.full_track_location = full_track_dir
            track_record.full_track_serial = new_full_track_record
            track_record.save()

            if os.path.exists(current_track_location):
                os.remove(current_track_location)

            temp_record.delete()

        except Exception as e:
            logger.error(
                f"Error creating YouTube track record for {temp_record.serial}: {str(e)}"
            )
            temp_record.record_status = 'failed'
            temp_record.save()

def delete_failed_music_temp_records():
    finished = False
    while not finished:
        temp_record = AddedFullTrackTemp.objects.filter(
            record_status='failed').first()
        
        try:
            file_location = os.path.join(temp_record.file_path,
                                         temp_record.serial + '.mp3')
            if os.path.exists(file_location):
                os.remove(file_location)
            temp_record.delete()
            
        except Exception as e:
            logger.error(f"Error deleting failed music temp record for {temp_record.serial}: {str(e)}")
            temp_record.record_status = 'failed deletion'
            temp_record.save()

def check_music_full_track():
    finished = False
    while not finished:
        full_track = AddedFullTrackTemp.objects.filter(
            record_status='pending',
            mp3_file_added=True
        ).first()

        if full_track is None:
            finished = True
            break

        try:
            track_record = MusicTrackRecord.objects.filter(
                serial=full_track.track.serial
            ).first()

            if track_record is None:
                raise ValueError(f"Track not found for full_track {full_track.serial}")

            compare_results = compare_tracks(
                ref_path=track_record.track_location,
                ref_serial=track_record.serial,
                test_path=full_track.file_path,
                test_serial=full_track.serial,
            ) 

            if compare_results['overall_similarity'] >= 0.8:
                full_track.record_status = 'completed'
            else:
                full_track.record_status = 'not matched'

            full_track.save()

        except Exception as e:
            logger.error(f"Error checking full track status: {str(e)}")
            full_track.record_status = 'failed'
            full_track.save()

def parse_article_json_file():
    finished = True
    while not finished:
        try:
            finished = True
            pass
        except Exception as e:
            logger.error(f"Error parsing article JSON file: {str(e)}")
            
def validate_scraper_links():
    finished = False
    while not finished:
            scraper_record = ScraperUploadFile.objects.filter(
                status='validating').first()
            if scraper_record is None:
                finished = True
                break

            try:
                path = scraper_record.file_location + scraper_record.serial + '.csv'
                df = pd.read_csv(path)
                
                for link in df['Links']:
                    if not link.startswith('https://www.face2facegames.com/'):
                        scraper_record.status = 'failed validation'
                        scraper_record.save()
                        break
                    else:
                        continue
                    
                scraper_record.status = 'validated'
                scraper_record.save()
            
            except Exception as e:
                scraper_record.status = 'failed validation'
                scraper_record.save()
                logger.error(f"Error validating scraper links: {str(e)}")

def run_scraper_jobs():
    finished = False
    while not finished:
        try:
            scraper_record = ScraperOutputFile.objects.filter(
                status='pending').first()
            if scraper_record is None:
                finished = True
                break
            
            scraper = ScraperUploadFile.objects.filter(
                serial=scraper_record.scraper_file.serial,
                user=scraper_record.user
            ).first()
            
            if scraper is None:
                scraper_record.status = 'failed'
                scraper_record.save()
                continue
            mtg_f2f_scraper(
                file_path=scraper.file_location,
                serial=scraper.serial,
                output_serial=scraper_record.serial,
                output_path=scraper_record.file_location
            )
            
            scraper_record.status = 'completed'
            scraper_record.save()
            
        except Exception as e:
            scraper.status = 'failed'
            scraper.save()
            logger.error(f"Error running scraper jobs: {str(e)}")

def resize_album_playlist_thumbnails():
    finished = False
    while not finished:
        album_record = MusicAlbumRecord.objects.filter(
            album_thumbnail_resized=False,
            album_thumbnail_resize_failed=False
        ).first()
        
        if album_record is None:
            finished = True
            break
        
        try:
            original_image_path = (
                album_record.album_image_location + f"{album_record.serial}.jpg"
            )

            if not os.path.exists(original_image_path):
                raise FileNotFoundError(f"Original image not found: {original_image_path}")

            with open('json/directory.json', 'r') as f:
                directory = json.load(f)

            list_view_thumbnail_dir = directory['music_list_view_thumbnail_dir']
            os.makedirs(list_view_thumbnail_dir, exist_ok=True)

            active_player_thumbnail_dir = directory['music_active_player_thumbnail_dir']
            os.makedirs(active_player_thumbnail_dir, exist_ok=True)

            with Image.open(original_image_path) as img:
                img = img.convert("RGB")

                list_view_size = (200, 200)
                list_view_img = img.copy()
                list_view_img.thumbnail(list_view_size, Image.LANCZOS)

                list_view_path = os.path.join(
                    list_view_thumbnail_dir,
                    f"{album_record.serial}.jpg"
                )
                list_view_img.save(list_view_path,
                                   "JPEG",
                                   quality=90,
                                   optimize=True)

                active_player_size = (400, 400)
                active_player_img = img.copy()
                active_player_img.thumbnail(active_player_size, Image.LANCZOS)

                active_player_path = os.path.join(
                    active_player_thumbnail_dir,
                    f"{album_record.serial}.jpg"
                )
                active_player_img.save(active_player_path,
                                       "JPEG",
                                       quality=90,
                                       optimize=True)

            album_record.album_thumbnail_resized = True
            album_record.list_view_thumbnail_location = list_view_thumbnail_dir
            album_record.active_player_thumbnail_location = active_player_thumbnail_dir
            album_record.save()

        except Exception as e:
            logger.error(f"Error resizing album and playlist thumbnails: {str(e)}")
            album_record.album_thumbnail_resize_failed = True
            album_record.save()

def process_admin_file_upload():
    finished = False
    while not finished:
        admin_file_record = AdminFileRecord.objects.filter(record_status='uploaded',
                                                           file_validated=False,
                                                           processed=False).first()
        try:
            if admin_file_record is None:
                finished = True
                break
            if admin_file_record.process == 'mtg_card_source':
                if admin_file_record.file_type == '.jsonl':
                    source_file = os.path.join(
                        admin_file_record.file_location,
                        f"{admin_file_record.serial}{admin_file_record.file_type}"
                    )
                    create_chunks = chunk_magic_data_file(file_path=source_file, chunk_size=500)
                    
                    if create_chunks is not True:
                        admin_file_record.record_status = 'processing_failed'
                        admin_file_record.processed = True
                        admin_file_record.save()
                        continue
                
                else:
                    admin_file_record.record_status = 'invalid_file_type'
                    admin_file_record.processed = True
                    admin_file_record.save()
                    continue
                
            else:
                admin_file_record.record_status = 'unknown_process'
                admin_file_record.processed = True
                admin_file_record.save()
                continue
            
            admin_file_record.file_validated = True
            admin_file_record.record_status = 'validated'
            admin_file_record.save()

        except Exception as e:
            logger.error(f"Error processing admin file upload: {str(e)}")

def handle_processed_admin_file():
    pass

def create_mtg_database():
    finished = False

    while not finished:
        mtg_temp_file = MagicTempFiles.objects.filter(file_status='pending').first()

        if mtg_temp_file is None:
            finished = True
            break

        try:
            mtg_file = os.path.join(
                mtg_temp_file.file_location,
                f"{mtg_temp_file.file_name}{mtg_temp_file.file_extension}"
            )

            with open(mtg_file, 'r') as f:
                cards = json.load(f)

            with open('json/directory.json', 'r') as f:
                directory = json.load(f)

            image_dir = directory['magic_card_image_dir']
            json_dir = directory['mtg_json_dir']
            os.makedirs(image_dir, exist_ok=True)
            os.makedirs(json_dir, exist_ok=True)

            for card in cards:
                try:
                    if MagicCards.objects.filter(card_id=card['id']).exists():
                        update_legalities = card.get('legalities')
                        new_sorted_legalities = legalities_sorter(update_legalities)
                        legalities_record = MagicCardLegalities.objects.filter(
                            card=card['id']).first()
                        
                        legalities_record.duel = new_sorted_legalities.get('duel')
                        legalities_record.brawl = new_sorted_legalities.get('brawl')
                        legalities_record.penny = new_sorted_legalities.get('penny')
                        legalities_record.predh = new_sorted_legalities.get('predh')
                        legalities_record.future = new_sorted_legalities.get('future')
                        legalities_record.legacy = new_sorted_legalities.get('legacy')
                        legalities_record.modern = new_sorted_legalities.get('modern')
                        legalities_record.pauper = new_sorted_legalities.get('pauper')
                        legalities_record.alchemy = new_sorted_legalities.get('alchemy')
                        legalities_record.pioneer = new_sorted_legalities.get('pioneer')
                        legalities_record.vintage = new_sorted_legalities.get('vintage')
                        legalities_record.historic = new_sorted_legalities.get('historic')
                        legalities_record.standard = new_sorted_legalities.get('standard')
                        legalities_record.timeless = new_sorted_legalities.get('timeless')
                        legalities_record.commander = new_sorted_legalities.get('commander')
                        legalities_record.gladiator = new_sorted_legalities.get('gladiator')
                        legalities_record.oldschool = new_sorted_legalities.get('oldschool')
                        legalities_record.premodern = new_sorted_legalities.get('premodern')
                        legalities_record.oathbreaker = new_sorted_legalities.get('oathbreaker')
                        legalities_record.standardbrawl = new_sorted_legalities.get('standardbrawl')
                        legalities_record.paupercommander = new_sorted_legalities.get('paupercommander')
                        legalities_record.update_date = timezone.now()
                        legalities_record.save()
                        
                        update_prices = card.get('prices')
                        new_sorted_prices = prices_sorter(update_prices)
                        prices_record = MagicCardPrices.objects.filter(
                            card=card['id']).first()
                        
                        prices_record.eur_price = new_sorted_prices.get('eur')
                        prices_record.tix_price = new_sorted_prices.get('tix')
                        prices_record.usd_price = new_sorted_prices.get('usd')
                        prices_record.eur_foil_price = new_sorted_prices.get('eur_foil')
                        prices_record.usd_foil_price = new_sorted_prices.get('usd_foil')
                        prices_record.usd_etched_price = new_sorted_prices.get('usd_etched')
                        prices_record.update_date = timezone.now()
                        prices_record.save()

                    front_url = None
                    back_url = None

                    if card.get("card_faces"):
                        faces = card["card_faces"]
                        front_url = faces[0].get("image_uris", {}).get("png")
                        if len(faces) > 1:
                            back_url = faces[1].get("image_uris", {}).get("png")

                    if not front_url:
                        front_url = card.get("image_uris", {}).get("png")
                    
                    try:
                        add_image = magic_image_downloader(
                            image_url=front_url,
                            image_url_back=back_url,
                            output_path=image_dir,
                            serial=card['id']
                        )
                        image_added = True
                        
                    except Exception as e:
                        logger.error(f"Error downloading image for card {card['id']}: {str(e)}")
                        image_added = False

                    back_exists = back_url is not None
                    back_serial = f"{card['id']}_1" if back_exists else None

                    cmc_value = card.get('cmc')
                    if isinstance(cmc_value, Decimal):
                        cmc_value = float(cmc_value)

                    data = {
                        "card_object": card.get('object'),
                        "oracle_id": card.get('oracle_id'),
                        "multiverse_ids": card.get('multiverse_ids'),
                        "mtgo_id": card.get('mtgo_id'),
                        "arena_id": card.get('arena_id'),
                        "tcgplayer_id": card.get('tcgplayer_id'),
                        "cardmarket_id": card.get('cardmarket_id'),
                        "card_name": card.get('name'),
                        "language": card.get('lang'),
                        "released_at": card.get('released_at'),
                        "card_uri": card.get('uri'),
                        "scryfall_uri": card.get('scryfall_uri'),
                        "layout": card.get('layout'),
                        "highres_image": card.get('highres_image'),
                        "image_status": card.get('image_status'),
                        "image_uris": card.get('image_uris'),
                        "mana_cost": card.get('mana_cost'),
                        "cmc": cmc_value,
                        "type_line": card.get('type_line'),
                        "oracle_text": card.get('oracle_text'),
                        "colors": card.get('colors'),
                        "color_identity": card.get('color_identity'),
                        "keywords": card.get('keywords'),
                        "legalities": card.get('legalities'),
                        "games": card.get('games'),
                        "produced_mana": card.get('produced_mana'),
                        "reserved": card.get('reserved'),
                        "game_changer": card.get('game_changer'),
                        "foil": card.get('foil'),
                        "non_foil": card.get('nonfoil'),
                        "finishes": card.get('finishes'),
                        "oversized": card.get('oversized'),
                        "promo": card.get('promo'),
                        "reprint": card.get('reprint'),
                        "variation": card.get('variation'),
                        "set_id": card.get('set_id'),
                        "set_code": card.get('set'),
                        "set_name": card.get('set_name'),
                        "set_type": card.get('set_type'),
                        "set_uri": card.get('set_uri'),
                        "set_search_uri": card.get('set_search_uri'),
                        "scryfall_set_uri": card.get('scryfall_set_uri'),
                        "rulings_uri": card.get('rulings_uri'),
                        "prints_search_uri": card.get('prints_search_uri'),
                        "collector_number": card.get('collector_number'),
                        "digital": card.get('digital'),
                        "rarity": card.get('rarity'),
                        "card_back_id": card.get('card_back_id'),
                        "artist": card.get('artist'),
                        "artist_ids": card.get('artist_ids'),
                        "illustration_id": card.get('illustration_id'),
                        "border_color": card.get('border_color'),
                        "frame": card.get('frame'),
                        "full_art": card.get('full_art'),
                        "textless": card.get('textless'),
                        "booster": card.get('booster'),
                        "story_spotlight": card.get('story_spotlight'),
                        "prices": card.get('prices'),
                        "related_uris": card.get('related_uris'),
                        "purchase_uris": card.get('purchase_uris'),
                        "mtgo_foil_id": card.get('mtgo_foil_id'),
                        "power": card.get('power'),
                        "toughness": card.get('toughness'),
                        "flavor_text": card.get('flavor_text'),
                        "edhrec_rank": card.get('edhrec_rank'),
                        "penny_rank": card.get('penny_rank'),
                        "printed_name": card.get('printed_name'),
                        "printed_type_line": card.get('printed_type_line'),
                        "printed_text": card.get('printed_text'),
                        "security_stamp": card.get('security_stamp'),
                        "all_parts": card.get('all_parts'),
                        "promo_types": card.get('promo_types'),
                        "loyalty": card.get('loyalty'),
                        "watermark": card.get('watermark'),
                        "frame_effects": card.get('frame_effects'),
                        "card_faces": card.get('card_faces'),
                        "preview": card.get('preview'),
                        "resource_id": card.get('resource_id'),
                        "color_indicator": card.get('color_indicator'),
                        "tcgplayer_etched_id": card.get('tcgplayer_etched_id'),
                        "content_warning": card.get('content_warning'),
                        "flavor_name": card.get('flavor_name'),
                        "attraction_lights": card.get('attraction_lights'),
                        "variation_of": card.get('variation_of'),
                        "life_modifier": card.get('life_modifier'),
                        "hand_modifier": card.get('hand_modifier'),
                        "defense": card.get('defense'),
                        "image_added": image_added,
                        "image_dir": image_dir,
                        "back_exists": back_exists,
                        "back_serial": back_serial,
                        "json_dir": json_dir,
                    }

                    card_json = {"card_id": card['id']}
                    for key, value in data.items():
                        if isinstance(value, Decimal):
                            card_json[key] = float(value)
                        elif hasattr(value, "isoformat"):
                            card_json[key] = value.isoformat()
                        else:
                            card_json[key] = value

                    data["card_json"] = card_json

                    new_card, created = MagicCards.objects.update_or_create(
                        card_id=card['id'], 
                        defaults=data)
                    new_card.save()

                    with open(os.path.join(json_dir, f"{card['id']}.json"), 'w') as json_file:
                        json.dump(card, json_file, indent=4)
                        
                    colors = card.get('colors')
                    get_colors = magic_color_identifier(colors)
                    color_identity = card.get('color_identity')
                    get_color_identity = magic_color_identifier(color_identity)
                        
                    new_card_view = MagicCardsView.objects.create(
                        card_id = new_card.card_id,
                        oracle_id = new_card.oracle_id,
                        card_name = new_card.card_name,
                        release_date = new_card.released_at,
                        mana_cost = new_card.mana_cost,
                        cmc = new_card.cmc,
                        type_line = new_card.type_line,
                        oracle_text = new_card.oracle_text,
                        colour_white = get_colors.get('W'),
                        colour_blue = get_colors.get('U'),
                        colour_black = get_colors.get('B'),
                        colour_red = get_colors.get('R'),
                        colour_green = get_colors.get('G'),
                        colour_colourless = get_colors.get('C'),
                        colour_identity_white = get_color_identity.get('W'),
                        colour_identity_blue = get_color_identity.get('U'),
                        colour_identity_black = get_color_identity.get('B'),
                        colour_identity_red = get_color_identity.get('R'),
                        colour_identity_green = get_color_identity.get('G'),
                        colour_identity_colourless = get_color_identity.get('C'),
                        reserved = new_card.reserved,
                        keywords = new_card.keywords,
                        foil = new_card.foil,
                        non_foil = new_card.non_foil,
                        set_name = new_card.set_name,
                        set_type = new_card.set_type,
                        collector_number = new_card.collector_number,
                        rarity = new_card.rarity,
                        power = new_card.power,
                        toughness = new_card.toughness,
                        flavor_text = new_card.flavor_text,
                        edh_rank = new_card.edhrec_rank,
                        penny_rank = new_card.penny_rank,
                        promo_types = new_card.promo_types,
                        loyalty = new_card.loyalty,
                        life_modifier = new_card.life_modifier,
                        produced_mana = new_card.produced_mana,
                        hand_modifier = new_card.hand_modifier,
                        defense = new_card.defense,
                        back_exists = new_card.back_exists,
                        back_serial = new_card.back_serial,
                        image_dir = new_card.image_dir,
                        image_added = new_card.image_added,
                        json_dir = new_card.json_dir,
                        create_date = timezone.now(),
                        update_date = timezone.now()
                    )
                    new_card_view.save()
                    
                    keywords = card.get('keywords')
                    for keyword in keywords:
                        serial = uuid.uuid1()
                        MagicCardKeywords.objects.create(
                            serial=serial,
                            card=new_card_view,
                            keyword=keyword,
                            create_date = timezone.now(),
                            update_date = timezone.now()
                        ).save()
                    
                    legalities = card.get('legalities')
                    sorted_legalities = legalities_sorter(legalities)
                    legalities_serial = uuid.uuid1()
                    
                    new_legalities_record = MagicCardLegalities.objects.create(
                        serial=legalities_serial,
                        card=new_card_view,
                        duel =sorted_legalities.get('duel'),
                        brawl = sorted_legalities.get('brawl'),
                        penny = sorted_legalities.get('penny'),
                        predh = sorted_legalities.get('predh'),
                        future = sorted_legalities.get('future'),
                        legacy = sorted_legalities.get('legacy'),
                        modern = sorted_legalities.get('modern'),
                        pauper = sorted_legalities.get('pauper'),
                        alchemy = sorted_legalities.get('alchemy'),
                        pioneer = sorted_legalities.get('pioneer'),
                        vintage = sorted_legalities.get('vintage'),
                        historic = sorted_legalities.get('historic'),
                        standard = sorted_legalities.get('standard'),
                        timeless = sorted_legalities.get('timeless'),
                        commander = sorted_legalities.get('commander'),
                        gladiator = sorted_legalities.get('gladiator'),
                        oldschool = sorted_legalities.get('oldschool'),
                        premodern = sorted_legalities.get('premodern'),
                        oathbreaker = sorted_legalities.get('oathbreaker'),
                        standardbrawl = sorted_legalities.get('standardbrawl'),
                        paupercommander = sorted_legalities.get('paupercommander'),
                        create_date = timezone.now(),
                        update_date = timezone.now()
                    )
                    new_legalities_record.save()
                    
                    card_prices = card.get('prices')
                    sorted_card_prices = prices_sorter(card_prices)
                    prices_serial = uuid.uuid1()
                    
                    new_card_price_record = MagicCardPrices.objects.create(
                        serial = prices_serial,
                        card = new_card_view,
                        eur_price = sorted_card_prices.get('eur'),
                        tix_price = sorted_card_prices.get('tix'),
                        usd_price = sorted_card_prices.get('usd'),
                        eur_foil_price = sorted_card_prices.get('eur_foil'),
                        usd_foil_price = sorted_card_prices.get('usd_foil'),
                        usd_etched_price = sorted_card_prices.get('usd_etched'),
                        create_date = timezone.now(),
                        update_date = timezone.now()
                    )
                    new_card_price_record.save()
                    
                    uris_serial = uuid.uuid1()
                    
                    magic_uris = MagicCardUris.objects.create(
                        serial = uris_serial,
                        card = new_card_view,
                        card_uri = new_card.card_uri,
                        scryfall_uri = new_card.scryfall_uri,
                        set_uri = new_card.set_uri,
                        set_search_uri = new_card.set_search_uri,
                        scryfall_set_uri = new_card.scryfall_set_uri,
                        rulings_uri = new_card.rulings_uri,
                        prints_search_uri = new_card.prints_search_uri,
                        related_uris = new_card.related_uris,
                        purchase_uris = new_card.purchase_uris,
                        image_uris = new_card.image_uris,
                        create_date = timezone.now(),
                        update_date = timezone.now()
                    )
                    magic_uris.save()
                    
                    misc_serial = uuid.uuid1()
                    
                    magic_cards_misc = MagicCardMiscData.objects.create(
                        serial = misc_serial,
                        card = new_card_view,
                        multiverse_ids = new_card.multiverse_ids,
                        arena_id = new_card.arena_id,
                        tcgplayer_id = new_card.tcgplayer_id,
                        cardmarket_id = new_card.cardmarket_id,
                        language = new_card.language,
                        layout = new_card.layout,
                        highres_image = new_card.highres_image,
                        image_status = new_card.image_status,
                        games = new_card.games,
                        finishes = new_card.finishes,
                        oversized = new_card.oversized,
                        promo = new_card.promo,
                        reprint = new_card.reprint,
                        variation = new_card.variation,
                        set_code = new_card.set_code,
                        digital = new_card.digital,
                        artist = new_card.artist,
                        artist_ids = new_card.artist_ids,
                        illustration_id = new_card.illustration_id,
                        border_color = new_card.border_color,
                        frame = new_card.frame,
                        full_art = new_card.full_art,
                        textless = new_card.textless,
                        booster = new_card.booster,
                        story_spotlight = new_card.story_spotlight,
                        mtgo_foil_id = new_card.mtgo_foil_id,
                        printed_name = new_card.printed_name,
                        printed_type_line = new_card.printed_type_line,
                        printed_text = new_card.printed_text,
                        security_stamp = new_card.security_stamp,
                        promo_types = new_card.promo_types,
                        watermark = new_card.watermark,
                        frame_effects = new_card.frame_effects,
                        card_faces = new_card.card_faces,
                        preview = new_card.preview,
                        resource_id = new_card.resource_id,
                        color_indicator = new_card.color_indicator,
                        tcgplayer_etched_id = new_card.tcgplayer_etched_id,
                        content_warning = new_card.content_warning,
                        flavor_name = new_card.flavor_name,
                        attraction_lights = new_card.attraction_lights,
                        variation_of = new_card.variation_of,
                        create_date = timezone.now(),
                        update_date = timezone.now()
                    )
                    magic_cards_misc.save()

                    mtg_temp_file.file_status = 'processed'
                    mtg_temp_file.save()
            
                except Exception as e:
                    logger.error(f"Error processing MTG temp file {card}: {str(e)}")
                

        except Exception as e:
            mtg_temp_file.file_status = 'failed'
            mtg_temp_file.failed_status = True
            mtg_temp_file.save()
            logger.error(f"Error creating MTG database: {str(e)}")
            
def handle_processed_mtg_temp_files():
    finished = False
    while not finished:
        mtg_processed_temp_file = MagicTempFiles.objects.filter(
            file_status='processed').first()

        if mtg_processed_temp_file is None:
            finished = True
            break
        
        try:
            file_location = os.path.join(
                mtg_processed_temp_file.file_location,
                f"{mtg_processed_temp_file.file_name}{mtg_processed_temp_file.file_extension}"
            )
            if os.path.exists(file_location):
                os.remove(file_location)
                
            create_completed_magic_record = CompletedTempFilesLog.objects.create(
                serial=str(uuid.uuid4()),
                file_name = mtg_processed_temp_file.file_name,
                file_location = mtg_processed_temp_file.file_location,
                file_extension = mtg_processed_temp_file.file_extension,
                process_status = 'completed - passed',
                run_number = mtg_processed_temp_file.run_number,
                create_date = timezone.now()
            )
            create_completed_magic_record.save()
            
            mtg_processed_temp_file.delete()

        except:
            mtg_processed_temp_file.file_status = 'failed post processing'
            mtg_processed_temp_file.update_date = timezone.now()
            mtg_processed_temp_file.save()

def handle_failed_mtg_temp_files():
    finished = False
    while not finished:
        mtg_failed_temp_file = MagicTempFiles.objects.filter(
            file_status='failed').first()

        if mtg_failed_temp_file is None:
            finished = True
            break
        
        try:
            file_location = os.path.join(
                mtg_failed_temp_file.file_location,
                f"{mtg_failed_temp_file.file_name}{mtg_failed_temp_file.file_extension}"
            )
            if os.path.exists(file_location):
                os.remove(file_location)
                
            create_failed_magic_record = CompletedTempFilesLog.objects.create(
                serial=str(uuid.uuid4()),
                file_name = mtg_failed_temp_file.file_name,
                file_location = mtg_failed_temp_file.file_location,
                file_extension = mtg_failed_temp_file.file_extension,
                process_status = 'completed - failed',
                run_number = mtg_failed_temp_file.run_number,
                create_date = timezone.now()
            )
            create_failed_magic_record.save()
            
            mtg_failed_temp_file.delete()

        except Exception as e:
            mtg_failed_temp_file.file_status = 'failed post processing'
            mtg_failed_temp_file.update_date = timezone.now()
            mtg_failed_temp_file.save()

        if mtg_failed_temp_file is None:
            finished = True
            break