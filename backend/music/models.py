from django.db import models

class MusicTempRecord(models.Model):
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    spotify_link = models.CharField(max_length=300, null=False)
    apple_link = models.CharField(max_length=300, null=False)
    failed_status = models.BooleanField(default=False, null=False)
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True, null=False)

    class Meta:
        db_table = 'music_temp_record'
        verbose_name = 'Music Temp Record'
        verbose_name_plural = 'Music Temp Records'

class ArtistRecord(models.Model):
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    artist_name = models.CharField(max_length=100, null=False)
    artist_image_location = models.CharField(max_length=300, null=False)
    artist_popularity = models.IntegerField(default=0, null=False)
    artist_followers = models.IntegerField(default=0, null=False)
    artist_spotify_link = models.CharField(max_length=300, null=False)
    create_date = models.DateTimeField(auto_now_add=True, null=False)
    
    class Meta:
        db_table = 'artist_record'
        verbose_name = 'Artist Record'
        verbose_name_plural = 'Artist Records'

class ArtistGenres(models.Model):
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    artist = models.ForeignKey(ArtistRecord, on_delete=models.CASCADE)
    genre = models.CharField(max_length=100, null=False)
    date_creted = models.DateTimeField(auto_now_add=True, null=False)
    
    class Meta:
        db_table = 'artist_genres'
        verbose_name = 'Artist Genre'
        verbose_name_plural = 'Artist Genres'

class MusicAlbumRecord(models.Model):
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    artist_record = models.ForeignKey(ArtistRecord, on_delete=models.CASCADE)
    album_name = models.CharField(max_length=100, null=False)
    album_image_location = models.CharField(max_length=300, null=False)
    album_popularity = models.IntegerField(default=0, null=False)
    album_type = models.CharField(max_length=100, null=False)
    release_date = models.DateTimeField(null=False)
    total_tracks = models.IntegerField(default=0, null=False)
    album_spotify_link = models.CharField(max_length=300, null=False)
    
    class Meta:
        db_table = 'music_album_record'
        verbose_name = 'Music Album Record'
        verbose_name_plural = 'Music Album Records'
        
class MusicTrackRecord(models.Model):
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    album_record = models.ForeignKey(MusicAlbumRecord, on_delete=models.CASCADE)
    artist_record = models.ForeignKey(ArtistRecord, on_delete=models.CASCADE)
    track_number = models.IntegerField(default=0, null=False)
    track_name = models.CharField(max_length=100, null=False)
    track_duration = models.IntegerField(default=0, null=False)
    track_location = models.CharField(max_length=300, null=False)
    
    class Meta:
        db_table = 'music_track_record'
        verbose_name = 'Music Track Record'
        verbose_name_plural = 'Music Track Records'
    
    
class AddedFullTrack(models.Model):
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    file = models.BooleanField(default=False, null=False)
    file_path = models.CharField(max_length=300, null=False)
    youtube_link = models.CharField(max_length=300, null=True)
    track = models.ForeignKey(MusicTrackRecord, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=100, default='pending', null=False)
    
    class Meta:
        db_table = 'added_full_track'
        verbose_name = 'Added Full Track'
        verbose_name_plural = 'Added Full Tracks'