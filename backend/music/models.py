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
    album_thumbnail_resized = models.BooleanField(default=False, null=False)
    album_thumbnail_resize_failed = models.BooleanField(default=False, null=False)
    list_view_thumbnail_location = models.CharField(max_length=300, null=True, default='')
    active_player_thumbnail_location = models.CharField(max_length=300, null=True, default='')
    create_date = models.DateTimeField(auto_now_add=True, null=False)
    last_updated_date = models.DateTimeField(auto_now=True, null=False)
    
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
    full_track_added = models.BooleanField(default=False, null=False)
    full_track_location = models.CharField(max_length=300, null=True, default='')
    full_track_serial = models.ForeignKey('MusicFullTrackRecord', on_delete=models.CASCADE, null=True)
    create_date = models.DateTimeField(auto_now_add=True, null=False)
    last_updated_date = models.DateTimeField(auto_now=True, null=False)
    
    class Meta:
        db_table = 'music_track_record'
        verbose_name = 'Music Track Record'
        verbose_name_plural = 'Music Track Records'
        
class AddedFullTrackTemp(models.Model):
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    track = models.ForeignKey(MusicTrackRecord, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    youtube_link = models.CharField(max_length=300, null=True)
    file_record = models.BooleanField(default=False, null=False)
    link_record = models.BooleanField(default=False, null=False)
    file_path = models.CharField(max_length=300, null=False)
    mp3_file_added = models.BooleanField(default=False, null=False)
    create_date = models.DateTimeField(auto_now_add=True, null=False)
    record_status = models.CharField(max_length=100, default='pending', null=False)
    
    class Meta:
        db_table = 'added_full_track_temp'
        verbose_name = 'Added Full Track Temp'
        verbose_name_plural = 'Added Full Track Temps'
        
class MusicFullTrackRecord(models.Model):
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    album = models.ForeignKey(MusicAlbumRecord, on_delete=models.CASCADE, null=True)
    track = models.ForeignKey(MusicTrackRecord, on_delete=models.CASCADE, null=True)
    track_location = models.CharField(max_length=300, null=False)
    create_date = models.DateTimeField(auto_now_add=True, null=False)
    
    class Meta:
        db_table = 'music_full_track_record'
        verbose_name = 'Music Full Track Record'
        verbose_name_plural = 'Music Full Track Records'

class CustomMusicPlayerSettings(models.Model):
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    order_playback = models.BooleanField(default=True, null=False)
    shuffle_playback = models.BooleanField(default=False, null=False)
    create_date = models.DateTimeField(auto_now_add=True, null=False)
    last_updated_date = models.DateTimeField(auto_now=True, null=False)
    
    class Meta:
        db_table = 'custom_music_player_settings'
        verbose_name = 'Custom Music Player Settings'
        verbose_name_plural = 'Custom Music Player Settings'
        
class CustomMusicPlaylist(models.Model):
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    playlist_name = models.CharField(max_length=100, null=False)
    playlist_description = models.TextField(null=True, default='')
    played = models.BooleanField(default=False, null=False)
    create_date = models.DateTimeField(auto_now_add=True, null=False)
    last_updated_date = models.DateTimeField(auto_now=True, null=False)

    class Meta:
        db_table = 'custom_music_playlist'
        verbose_name = 'Custom Music Playlist'
        verbose_name_plural = 'Custom Music Playlists'
        
class CustomMusicPlaylistRecord(models.Model):
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    playlist = models.ForeignKey(CustomMusicPlaylist, on_delete=models.CASCADE)
    track = models.ForeignKey(MusicTrackRecord, on_delete=models.CASCADE)
    play_order = models.IntegerField(default=0, null=False)
    current_track = models.BooleanField(default=False, null=False)
    track_play_stop_time = models.FloatField(default=0.0, null=False)
    added_date = models.DateTimeField(auto_now_add=True, null=False)
    
    class Meta:
        db_table = 'custom_music_playlist_record'
        verbose_name = 'Custom Music Playlist Record'
        verbose_name_plural = 'Custom Music Playlist Records'