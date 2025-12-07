from django.db import models
from django.utils import timezone
from datetime import timedelta

class TempVideo(models.Model):
    serial = models.CharField(max_length=100, unique=True, null=False, primary_key=True)
    master_serial = models.CharField(max_length=100, null=False, unique=False)
    existing_series_serial = models.CharField(max_length=100, null=True, unique=False)
    video_name = models.CharField(max_length=100, null=False)
    title = models.CharField(max_length=100, default="", null=True)
    video_location = models.CharField(max_length=300, null=False)
    thumbnail_location = models.CharField(max_length=300, null=False)
    image_added = models.BooleanField(default=False, null=False)
    imdb_link = models.CharField(max_length=300, default="", null=False)
    imdb_rating = models.FloatField(default=0, null=True)
    imdb_link_failed = models.BooleanField(default=False, null=True)
    failed_attempts = models.IntegerField(default=0, null=False)
    imdb_failed_attempts = models.IntegerField(default=0, null=False)
    main_tag = models.CharField(max_length=100, default="", null=True)
    age_rating = models.CharField(max_length=100, default="", null=True)
    tags = models.JSONField(default=list, null=True)
    directors = models.JSONField(default=list, null=True)
    stars = models.JSONField(default=list, null=True)
    writers = models.JSONField(default=list, null=True)
    creators = models.JSONField(default=list, null=True)
    permission = models.IntegerField(default=1, null=False)
    rating = models.FloatField(default=0, null=True)
    series = models.BooleanField(default=False, null=False)
    private = models.BooleanField(default=False, null=False)
    uploaded_by = models.ForeignKey('user.Credentials', on_delete=models.CASCADE, related_name='temp_videos', default=None, null=False)
    total_rating_score = models.FloatField(default=0, null=False)
    total_ratings = models.IntegerField(default=0, null=False)
    visual_profile = models.JSONField(default=dict, null=True)
    audio_profile = models.JSONField(default=dict, null=True)
    visual_details = models.JSONField(default=dict, null=True)
    audio_details = models.JSONField(default=dict, null=True)
    current_status = models.CharField(max_length=100, default="F", null=False)
    uploaded_date = models.DateTimeField(auto_now_add=True, null=False)
    last_updated = models.DateTimeField(auto_now=True, null=False)
    description = models.TextField(default="", null=True)
    genre_updated = models.BooleanField(default=True)
    season = models.IntegerField(default=0, null=False)
    episode = models.IntegerField(default=0, null=False)
    existing_series = models.BooleanField(default=False, null=False)
    corruption_check_temp = models.BooleanField(default=False, null=False)
    format_conversion = models.BooleanField(default=False, null=False)
    corruption_check_data = models.BooleanField(default=False, null=False)
    imdb_added = models.BooleanField(default=False, null=False)
    image_added = models.BooleanField(default=False, null=False)
    identifier_checked = models.BooleanField(default=False, null=False)
    visual_data_added = models.BooleanField(default=False, null=False)
    audio_data_added = models.BooleanField(default=False, null=False)
    upload_success = models.BooleanField(default=True, null=False)
    temp_video_location = models.CharField(max_length=300, default="", null=False)
    temp_video_extension = models.CharField(max_length=10, default="", null=False)
    
    def __str__(self):
        return self.video_name + " - " + str(self.rating)
    
    class Meta:
        db_table = 'temp_video'
        verbose_name = 'Temp Video'
        verbose_name_plural = 'Temp Videos'
        
class Video(models.Model):
    serial = models.CharField(max_length=100, null=False, unique=True, primary_key=True)
    series = models.BooleanField(default=False, null=False)
    total_seasons = models.IntegerField(default=0, null=False)
    total_episodes = models.IntegerField(default=0, null=False)
    title = models.CharField(max_length=100, default="", null=False)
    season_metadata = models.JSONField(default=dict, null=True)
    imdb_link = models.CharField(max_length=300, default="", null=False)
    imdb_rating = models.FloatField(default=0, null=False)
    main_tag = models.CharField(max_length=100, default="", null=False)
    permission = models.IntegerField(default=1, null=False)
    rating = models.FloatField(default=0, null=False)
    private = models.BooleanField(default=False, null=False)
    uploaded_by = models.ForeignKey('user.Credentials', on_delete=models.CASCADE, related_name='videos', default=None, null=False)
    total_rating_score = models.FloatField(default=0, null=False)
    total_ratings = models.IntegerField(default=0, null=False)
    uploaded_date = models.DateTimeField(auto_now_add=True, null=False)
    last_updated = models.DateTimeField(auto_now=True, null=False)
    description = models.TextField(default="", null=False)
    thumbnail_location = models.CharField(max_length=300, null=False)
    genre_updated = models.BooleanField(default=True, null=False)
    update_series = models.BooleanField(default=False, null=False)
    current_status = models.CharField(max_length=100, default="F", null=False)

    def __str__(self):
        return self.title + " - " + str(self.uploaded_by)

    class Meta:
        db_table = 'video'
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'
    
    def delete_related_records(self):
        if self.current_status == "D":
            self.video_record.all().delete()
            self.comments.all().delete()
            self.history.all().delete()
            self.delete()
            
class CustomVideoList(models.Model):
    list_serial = models.CharField(max_length=100, unique=True, primary_key=True, null=False)
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE, related_name='custom_list')
    list_name = models.CharField(max_length=100, null=False)
    create_date = models.DateTimeField(auto_now_add=True, null=False)
    last_updated = models.DateTimeField(auto_now=True, null=False)
    
    class Meta:
        db_table = 'custom_video_list'
        verbose_name = 'Custom Video List'
        verbose_name_plural = 'Custom Video Lists'

class CustomVideoListRecords(models.Model):
    video_serial = models.ForeignKey('Video', on_delete=models.CASCADE, related_name='custom_list_records', default=None, null=False)
    list_serial = models.ForeignKey('CustomVideoList', on_delete=models.CASCADE, related_name='custom_list_records', default=None, null=False)
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE, related_name='custom_list_records', default=None, null=False)
    date_added = models.DateTimeField(auto_now_add=True, null=False)
    
    class Meta:
        db_table = 'custom_video_list_records'
        verbose_name = 'Custom Video List Record'
        verbose_name_plural = 'Custom Video List Records'

class VideoTags(models.Model):
    tag = models.CharField(max_length=100, null=False)
    video = models.ForeignKey('Video', on_delete=models.CASCADE, related_name='video_tags', default=None, null=False)
    tag_updated = models.BooleanField(default=False, null=False)

    class Meta:
        db_table = 'video_tags'
        verbose_name = 'Video Tag'
        verbose_name_plural = 'Video Tags'

class VideoDirectors(models.Model):
    director = models.CharField(max_length=100, null=False)
    video = models.ForeignKey('Video', on_delete=models.CASCADE, related_name='video_directors', default=None, null=False)

    class Meta:
        db_table = 'video_directors'
        verbose_name = 'Video Director'
        verbose_name_plural = 'Video Directors'

class VideoStars(models.Model):
    star = models.CharField(max_length=100, null=False)
    video = models.ForeignKey('Video', on_delete=models.CASCADE, related_name='video_stars', default=None, null=False)

    class Meta:
        db_table = 'video_stars'
        verbose_name = 'Video Star'
        verbose_name_plural = 'Video Stars'

class VideoWriters(models.Model):
    writer = models.CharField(max_length=100, null=False)
    video = models.ForeignKey('Video', on_delete=models.CASCADE, related_name='video_writers', default=None, null=False)

    class Meta:
        db_table = 'video_writers'
        verbose_name = 'Video Writer'
        verbose_name_plural = 'Video Writers'

class VideoCreators(models.Model):
    creator = models.CharField(max_length=100, null=False)
    video = models.ForeignKey('Video', on_delete=models.CASCADE, related_name='video_creators', default=None, null=False)

    class Meta:
        db_table = 'video_creators'
        verbose_name = 'Video Creator'
        verbose_name_plural = 'Video Creators'

class VideoRecord(models.Model):
    master_record = models.ForeignKey('Video', on_delete=models.CASCADE, related_name='video_record', default=None, null=False)
    video_serial = models.CharField(max_length=100, null=False, unique=True, primary_key=True)
    video_location = models.CharField(max_length=300, null=False)
    video_name = models.CharField(max_length=100, null=False)
    visual_profile = models.JSONField(default=dict, null=True)
    audio_profile = models.JSONField(default=dict, null=True)
    visual_details = models.JSONField(default=dict, null=True)
    audio_details = models.JSONField(default=dict, null=True)
    series = models.BooleanField(default=False, null=False)
    season = models.IntegerField(default=0, null=False)
    episode = models.IntegerField(default=0, null=False)
    current_status = models.CharField(max_length=100, default="F", null=False)
    uploaded_date = models.DateTimeField(auto_now_add=True, null=False)
    last_updated = models.DateTimeField(auto_now=True, null=False)
    
    def __str__(self):
        return self.video_name + " - " + str(self.master_record)
    
    class Meta:
        db_table = 'video_record'
        verbose_name = 'Video Record'
        verbose_name_plural = 'Video Records'

class VideoComments(models.Model):
    master_record = models.ForeignKey('Video', on_delete=models.CASCADE, related_name='comments', default=None, null=False)
    serial = models.ForeignKey('VideoRecord', on_delete=models.CASCADE, related_name='comments', default=None, null=False)
    commenter = models.ForeignKey('user.Credentials', on_delete=models.CASCADE, related_name='video_comments', default=None, null=False)
    comment = models.TextField(null=False)
    comment_date = models.DateTimeField(auto_now_add=True, null=False)
    last_updated = models.DateTimeField(auto_now=True, null=False)

    def __str__(self):
        return self.comment + " - " + str(self.commenter)

    class Meta:
        db_table = 'video_comments'
        verbose_name = 'Video Comment'
        verbose_name_plural = 'Video Comments'

class VideoHistory(models.Model):
    master_record = models.ForeignKey('Video', on_delete=models.CASCADE, related_name='history', default=None, null=False)
    serial = models.ForeignKey('VideoRecord', on_delete=models.CASCADE, related_name='history', default=None, null=False)
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE, related_name='video_history', default=None, null=False)
    video_stop_time = models.FloatField(default=0, null=False)
    last_updated = models.DateTimeField(auto_now=True, null=False)
    
    class Meta:
        db_table = 'video_history'
        verbose_name = 'Video History'
        verbose_name_plural = 'Video Histories'

class VideoRating(models.Model):
    master_record = models.ForeignKey('Video', on_delete=models.CASCADE, related_name='ratings', default=None, null=False)
    serial = models.ForeignKey('VideoRecord', on_delete=models.CASCADE, related_name='ratings', default=None, null=False)
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE, related_name='video_ratings', default=None, null=False)
    rating = models.FloatField(default=0, null=False)
    rated_date = models.DateTimeField(auto_now_add=True, null=False)
    last_updated = models.DateTimeField(auto_now=True, null=False)

    class Meta:
        db_table = 'video_rating'
        verbose_name = 'Video Rating'
        verbose_name_plural = 'Video Ratings'
        
class VideoGenre(models.Model):
    genre = models.CharField(max_length=100, unique=True, primary_key=True)
    number_of_public_records = models.IntegerField(default=0, null=False)
    custom = models.BooleanField(default=False, null=False)
    
    class Meta:
        db_table = 'video_genre'
        verbose_name = 'Video Genre'
        verbose_name_plural = 'Video Genres'

class MyVideoList(models.Model):
    list_serial = models.CharField(max_length=100, unique=True, primary_key=True, null=False)
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE, related_name='my_list')
    list_name = models.CharField(max_length=100, null=False)
    vidoes = models.JSONField(default=list, null=False)
    create_date = models.DateTimeField(auto_now_add=True, null=False)
    last_updated = models.DateTimeField(auto_now=True, null=False)
    
    class Meta:
        db_table = 'my_video_list'
        verbose_name = 'My Video List'
        verbose_name_plural = 'My Video Lists'

class VideoFavourites(models.Model):
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE, related_name='favourites', null=False)
    video = models.ForeignKey('Video', on_delete=models.CASCADE, related_name='favourites', null=False)
    create_date = models.DateTimeField(auto_now_add=True, null=False)
    last_updated = models.DateTimeField(auto_now=True, null=False)
    
    class Meta:
        db_table = 'video_favourites'
        verbose_name = 'Video Favourite'
        verbose_name_plural = 'Video Favourites'

class FailedVideoRecords(models.Model):
    video_name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, default="")
    video_location = models.CharField(max_length=300)
    thumbnail_location = models.CharField(max_length=300)
    image_added = models.BooleanField(default=False)
    imdb_link = models.CharField(max_length=300, default="")
    imdb_rating = models.FloatField(default=0)
    imdb_link_failed = models.BooleanField(default=False)
    failed_attempts = models.IntegerField(default=0)
    imdb_failed_attempts = models.IntegerField(default=0)
    main_tag = models.CharField(max_length=100, default="")
    tags = models.JSONField(default=list)
    directors = models.JSONField(default=list)
    stars = models.JSONField(default=list)
    writers = models.JSONField(default=list)
    creators = models.JSONField(default=list)
    permission = models.IntegerField(default=1)
    rating = models.FloatField(default=0)
    series = models.BooleanField(default=False)
    private = models.BooleanField(default=False)
    uploaded_by = models.ForeignKey('user.Credentials', on_delete=models.CASCADE, related_name='failed_video_records', default=None)
    total_rating_score = models.FloatField(default=0)
    total_ratings = models.IntegerField(default=0)
    visual_profile = models.JSONField(default=dict)
    audio_profile = models.JSONField(default=dict)
    visual_details = models.JSONField(default=dict)
    audio_details = models.JSONField(default=dict)
    current_status = models.CharField(max_length=100, default="F")
    uploaded_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    description = models.TextField(default="")
    genre_updated = models.BooleanField(default=True)
    serial = models.CharField(max_length=100, unique=True)
    master_serial = models.CharField(max_length=100, null=True)
    season = models.IntegerField(default=0)
    episode = models.IntegerField(default=0)
    existing_series = models.BooleanField(default=False)
    corruption_check_temp = models.BooleanField(default=False)
    format_conversion = models.BooleanField(default=False)
    corruption_check_data = models.BooleanField(default=False)
    imdb_added = models.BooleanField(default=False)
    image_added = models.BooleanField(default=False)
    visual_data_added = models.BooleanField(default=False)
    audio_data_added = models.BooleanField(default=False)
    upload_success = models.BooleanField(default=True)
    temp_video_location = models.CharField(max_length=300, default="")
    temp_video_extension = models.CharField(max_length=10, default="")
    failed_video_location = models.CharField(max_length=300, default="")
    
    def __str__(self):
        return self.video_name + " - " + str(self.rating)

    class Meta:
        db_table = 'failed_video_records'
        verbose_name = 'Failed Video Record'
        verbose_name_plural = 'Failed Video Records'
        
class VideoQuery(models.Model):
    query_id = models.CharField(max_length=100, unique=True, primary_key=True)
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE, related_name='video_queries', null=False)
    query_date = models.DateTimeField(auto_now_add=True)
    video_exact_genre = models.JSONField(default=list)
    video_similar_genre = models.JSONField(default=list)
    video_exact_stars = models.JSONField(default=list)
    video_similar_stars = models.JSONField(default=list)
    video_exact_directors = models.JSONField(default=list)
    video_similar_directors = models.JSONField(default=list)
    video_exact_writers = models.JSONField(default=list)
    video_similar_writers = models.JSONField(default=list)
    video_exact_creators = models.JSONField(default=list)
    video_similar_creators = models.JSONField(default=list)
    delete_date = models.DateTimeField(null=False)
    
    class Meta:
        db_table = 'video_query'
        verbose_name = 'Video Query'
        verbose_name_plural = 'Video Queries'
        
class VideoRequest(models.Model):
    serial = models.CharField(max_length=100, unique=True, primary_key=True, null=False)
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE, related_name='video_requests', null=False)
    request_date = models.DateTimeField(auto_now_add=True)
    request_title = models.CharField(max_length=100, null=False)
    request_description = models.TextField(null=False)
    request_status = models.CharField(max_length=100, default="Pending", null=False)
    request_last_updated = models.DateTimeField(auto_now=True, null=False)
    reviewed_by = models.ForeignKey('user.AdminCredentials', on_delete=models.CASCADE, related_name='reviewed_video_requests', null=True, blank=True)
    
    class Meta:
        db_table = 'video_request'
        verbose_name = 'Video Request'
        verbose_name_plural = 'Video Requests'