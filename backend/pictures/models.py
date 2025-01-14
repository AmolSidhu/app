from django.db import models
from datetime import datetime, timedelta

class Picture(models.Model):
    uploaded_by = models.ForeignKey('user.Credentials', on_delete=models.CASCADE, null=False)
    picture_serial = models.CharField(max_length=100, null=False, primary_key=True)
    picture_pathway = models.CharField(max_length=100, null=False)
    thumbnail_pathway = models.CharField(max_length=100, null=False)
    backup_path = models.CharField(max_length=100, null=False)
    original_image_extension = models.CharField(max_length=100, null=False)
    full_backup_path = models.CharField(max_length=100, default='', null=False)
    picture_name = models.CharField(max_length=100, null=False)
    picture_title = models.CharField(max_length=100, null=False)
    date_uploaded = models.DateTimeField(auto_now_add=True, null=False)
    description = models.TextField(null=True)
    last_updated = models.DateTimeField(auto_now=True, null=False)
    current_status = models.CharField(max_length=100, default='A', null=False)
    album_pathway = models.CharField(max_length=100, null=False)
    album = models.ForeignKey('DefaultAlbums', on_delete=models.CASCADE, null=False)
    picture_editable = models.BooleanField(default=False, null=False)
    
    class Meta:
        db_table = 'pictures'
        verbose_name = 'Picture'
        verbose_name_plural = 'Pictures'

class MyAlbums(models.Model):
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE, null=False)
    album_name = models.CharField(max_length=100, null=False)
    album_serial = models.CharField(max_length=100, unique=True, primary_key=True, null=False)
    album_description = models.TextField(null=True)
    album_status = models.CharField(max_length=100, default='A', null=False)
    album_data = models.JSONField(default=dict, null=False)
    date_created = models.DateTimeField(auto_now_add=True, null=False)
    last_updated = models.DateTimeField(auto_now=True, null=False)
    album_pathway = models.CharField(max_length=100, null=False)
    
    class Meta:
        db_table = 'my_albums'
        verbose_name = 'My Album'
        verbose_name_plural = 'My Albums'
        
class MyAlbumPictures(models.Model):
    album = models.ForeignKey('MyAlbums', on_delete=models.CASCADE, null=False)
    picture = models.ForeignKey('Picture', on_delete=models.CASCADE, null=False)
    last_updated = models.DateTimeField(auto_now=True, null=False)
    date_added = models.DateTimeField(auto_now_add=True, null=False)
    
    class Meta:
        db_table = 'my_album_pictures'
        verbose_name = 'My Album Picture'
        verbose_name_plural = 'My Album Pictures'
    
class DefaultAlbums(models.Model):
    album_name = models.CharField(max_length=100, null=False)
    album_serial = models.CharField(max_length=100, unique=True, primary_key=True, null=False)
    album_description = models.TextField(null=True)
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE, null=False)
    album_status = models.CharField(max_length=100, default='A', null=False)
    album_data = models.JSONField(default=dict, null=False)
    date_created = models.DateTimeField(auto_now_add=True, null=False)
    last_updated = models.DateTimeField(auto_now=True, null=False)
    album_pathway = models.CharField(max_length=100, default='', null=False)
    
    class Meta:
        db_table = 'default_albums'
        verbose_name = 'Default Album'
        verbose_name_plural = 'Default Albums'

class FavouritePictures(models.Model):
    serial = models.CharField(max_length=100, unique=True, primary_key=True, null=False)
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE, null=False)
    picture = models.ForeignKey('Picture', on_delete=models.CASCADE, null=False)
    date_added = models.DateTimeField(auto_now_add=True, null=False)
    
    class Meta:
        db_table = 'favourite_images'
        verbose_name = 'Favourite Image'
        verbose_name_plural = 'Favourite Images'
        
class ImageQueryTable(models.Model):
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE, null=False)
    current_album = models.ForeignKey('DefaultAlbums', on_delete=models.CASCADE, null=False)
    query_id = models.CharField(max_length=100, unique=True, primary_key=True)
    only_current_album = models.BooleanField(default=False, null=False)
    only_favourites = models.BooleanField(default=False, null=False)
    similar_tags = models.JSONField(default=dict, null=False)
    similar_people = models.JSONField(default=dict, null=False)
    exact_tags = models.JSONField(default=dict, null=False)
    exact_people = models.JSONField(default=dict, null=False)
    date_created = models.DateTimeField(auto_now_add=True, null=False)
    date_to_be_deleted = models.DateTimeField(default=(datetime.now() + timedelta(days=1)), null=False)
    
    class Meta:
        db_table = 'image_query_table'
        verbose_name = 'Image Query Table'
        verbose_name_plural = 'Image Query Tables'

class ImageTags(models.Model):
    picture = models.ForeignKey('Picture', on_delete=models.CASCADE, null=False, to_field='picture_serial')
    album = models.ForeignKey('DefaultAlbums', on_delete=models.CASCADE, null=False)
    tag = models.CharField(max_length=100, null=False)
    date_added = models.DateTimeField(auto_now_add=True, null=False)
    
    class Meta:
        db_table = 'image_tags'
        verbose_name = 'Image Tag'
        verbose_name_plural = 'Image Tags'
        
class ImagePeopleTags(models.Model):
    picture = models.ForeignKey('Picture', on_delete=models.CASCADE, null=False, to_field='picture_serial')
    album = models.ForeignKey('DefaultAlbums', on_delete=models.CASCADE, null=False)
    person = models.CharField(max_length=100, null=False)
    date_added = models.DateTimeField(auto_now_add=True, null=False)
    
    class Meta:
        db_table = 'image_people_tags'
        verbose_name = 'Image People Tag'
        verbose_name_plural = 'Image People Tags'
        
class PictureQuery(models.Model):
    query_id = models.CharField(max_length=100, unique=True, primary_key=True, null=False)
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE, null=False)
    query_date = models.DateTimeField(auto_now_add=True, null=False)
    picture_exact_tags = models.JSONField(default=dict, null=False)
    picture_exact_people = models.JSONField(default=dict, null=False)
    picture_similar_tags = models.JSONField(default=dict, null=False)
    picture_similar_people = models.JSONField(default=dict, null=False)
    delete_date = models.DateTimeField(default=(datetime.now() + timedelta(days=1)), null=False)
    
    class Meta:
        db_table = 'picture_query'
        verbose_name = 'Picture Query'
        verbose_name_plural = 'Picture Queries'
