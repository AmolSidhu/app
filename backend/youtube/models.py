from django.db import models

class YoutubeLists(models.Model):
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    name = models.CharField(max_length=100, null=False)
    description = models.TextField(null=False)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    
class YoutubeListRecord(models.Model):
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    youtube_list = models.ForeignKey(YoutubeLists, on_delete=models.CASCADE)
    youtube_video = models.ForeignKey('videos.VideoRecord', on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('youtube_list', 'youtube_video')

class YoutubeVideoRecord(models.Model):
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    title = models.CharField(max_length=100, null=False)
    description = models.TextField(null=False)
    thumbnail = models.CharField(max_length=300, null=False)
    video_id = models.CharField(max_length=100, null=False)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)

class YoutubeVideoHistory(models.Model):
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    youtube_video = models.ForeignKey(YoutubeVideoRecord, on_delete=models.CASCADE)
    video_stop_time = models.FloatField(null=False)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'youtube_video')