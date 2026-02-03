from django.db import models

class YoutubeTempRecord(models.Model):
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    youtube_link = models.CharField(max_length=300, null=False)
    youtube_video_location = models.CharField(max_length=300, null=False)
    youtube_thumbnail_location = models.CharField(max_length=300, null=False)
    add_to_playlists = models.JSONField(default=dict)
    create_date = models.DateTimeField(auto_now_add=True)
    failed_status = models.BooleanField(default=False)
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'youtube_temp_record'
        verbose_name = 'Youtube Temp Record'
        verbose_name_plural = 'Youtube Temp Records'

class YoutubeLists(models.Model):
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    name = models.CharField(max_length=100, null=False)
    description = models.TextField(null=False)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'youtube_lists'
        verbose_name = 'Youtube List'
        verbose_name_plural = 'Youtube Lists'
    
class YoutubeListRecord(models.Model):
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    youtube_list = models.ForeignKey(YoutubeLists, on_delete=models.CASCADE)
    youtube_video = models.ForeignKey('youtube.YoutubeVideoRecord', on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'youtube_list_record'
        verbose_name = 'Youtube List Record'
        verbose_name_plural = 'Youtube List Records'

class YoutubeVideoRecord(models.Model):
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    title = models.CharField(max_length=100, null=False)
    description = models.TextField(null=False)
    thumbnail_path = models.CharField(max_length=300, null=False)
    video_path = models.CharField(max_length=300, null=False)
    video_id = models.CharField(max_length=100, null=False)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    analytics_record = models.BooleanField(default=False)
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'youtube_video_record'
        verbose_name = 'Youtube Video Record'
        verbose_name_plural = 'Youtube Video Records'

class YoutubeVideoHistory(models.Model):
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    youtube_video = models.ForeignKey(YoutubeVideoRecord, on_delete=models.CASCADE)
    video_stop_time = models.FloatField(null=False)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'youtube_video_history'
        verbose_name = 'Youtube Video History'
        verbose_name_plural = 'Youtube Video Histories'

class YoutubeVideoComments(models.Model):
    youtube_video = models.ForeignKey(YoutubeVideoRecord, on_delete=models.CASCADE)
    comment = models.TextField(null=False)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'youtube_video_comments'
        verbose_name = 'Youtube Video Comment'
        verbose_name_plural = 'Youtube Video Comments'
        
class YoutubeVideoLikes(models.Model):
    youtube_video = models.ForeignKey(YoutubeVideoRecord, on_delete=models.CASCADE)
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    video_rating =models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'youtube_video_likes'
        verbose_name = 'Youtube Video Like'
        verbose_name_plural = 'Youtube Video Likes'
        
class YoutubeVideoAnalytics(models.Model):
    youtube_video = models.ForeignKey(YoutubeVideoRecord, on_delete=models.CASCADE)
    video_visual_profile = models.JSONField(default=dict)
    video_audio_profile = models.JSONField(default=dict)
    video_emotion_profile = models.JSONField(default=dict)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'youtube_video_analytics'
        verbose_name = 'Youtube Video Analytic'
        verbose_name_plural = 'Youtube Video Analytics'

class YoutubeWatchLater(models.Model):
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    youtube_video = models.ForeignKey(YoutubeVideoRecord, on_delete=models.CASCADE)
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'youtube_watch_later'
        verbose_name = 'Youtube Watch Later'
        verbose_name_plural = 'Youtube Watch Laters'

class YoutubeFavourites(models.Model):
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    youtube_video = models.ForeignKey(YoutubeVideoRecord, on_delete=models.CASCADE)
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'youtube_favourites'
        verbose_name = 'Youtube Favourite'
        verbose_name_plural = 'Youtube Favourites'

class YoutubeVideoMetadata(models.Model):
    youtube_video = models.ForeignKey(YoutubeVideoRecord, on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    video_id = models.CharField(max_length=100, null=False, unique=True, primary_key=True)
    full_title = models.CharField(max_length=200, null=False)
    alt_title = models.CharField(max_length=200, null=True, blank=True)
    uploader = models.CharField(max_length=100, null=True, blank=True)
    uploader_id = models.CharField(max_length=100, null=True, blank=True)
    uploader_url = models.CharField(max_length=300, null=True, blank=True)
    video_license = models.CharField(max_length=100, null=True, blank=True)
    creators = models.JSONField(default=list, blank=True)
    upload_time = models.BigIntegerField(null=True, blank=True)
    upload_date = models.CharField(max_length=20, null=True, blank=True)
    release_time = models.BigIntegerField(null=True, blank=True)
    release_date = models.CharField(max_length=20, null=True, blank=True)
    modified_timestamp = models.BigIntegerField(null=True, blank=True)
    modified_date = models.CharField(max_length=20, null=True, blank=True)
    channel = models.CharField(max_length=100, null=True, blank=True)
    channel_id = models.CharField(max_length=100, null=True, blank=True)
    channel_url = models.CharField(max_length=300, null=True, blank=True)
    duration = models.BigIntegerField(null=True, blank=True)
    duration_formatted = models.CharField(max_length=20, null=True, blank=True)
    age_limit = models.IntegerField(null=True, blank=True)
    media_type = models.CharField(max_length=50, null=True, blank=True)
    tags = models.JSONField(default=list, blank=True)
    categories = models.JSONField(default=list, blank=True)
    
    class Meta:
        db_table = 'youtube_video_metadata'
        verbose_name = 'Youtube Video Metadata'
        verbose_name_plural = 'Youtube Video Metadatas'