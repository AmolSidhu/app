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