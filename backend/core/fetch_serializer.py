from rest_framework import serializers

from pictures.models import DefaultAlbums, Picture, MyAlbums
from videos.models import Video

class PictureFetchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Picture
        fields = ['picture_serial', 'picture_title',
                  'description','picture_editable']
        
class PicturePopupData(serializers.ModelSerializer):
    class Meta:
        model = Picture
        fields = ['picture_title', 'description']

class DefaultAlbumFetchSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefaultAlbums
        fields = ['album_serial', 'album_name',
                  'album_description']

class MyAlbumsFetchSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyAlbums
        fields = ['album_serial', 'album_name',
                  'album_description']

class VideoFetchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['title', 'description',
                  'uploaded_date', 'serial'] 