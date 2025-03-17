from rest_framework import serializers

from pictures.models import DefaultAlbums, Picture, MyAlbums, PictureQuery
from user.models import Credentials
from videos.models import Video, TempVideo, VideoRecord, FailedVideoRecords, VideoQuery, CustomVideoList
from management.models import Identifier, IdentifierTempTable

class PictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Picture
        fields = '__all__'

class DefaultAlbumsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefaultAlbums
        fields = '__all__'

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'

class TempVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TempVideo
        fields = '__all__'

class IdentifierTempTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdentifierTempTable
        fields = '__all__'
        
class IdentifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Identifier
        fields = '__all__'
        
class CredentialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credentials
        fields = '__all__'

class MyAlbumsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyAlbums
        fields = '__all__'

class TempVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TempVideo
        fields = '__all__'
        
class VideoRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoRecord
        fields = '__all__'

class FailedVideoRecordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FailedVideoRecords
        fields = '__all__'

class VideoQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoQuery
        fields = '__all__'
        
class PictureQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = PictureQuery
        fields = '__all__'
        
class CustomVideoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomVideoList
        fields = '__all__'