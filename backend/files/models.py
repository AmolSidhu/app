from django.db import models

class ShareFolder(models.Model):
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    folder_name = models.CharField(max_length=100, null=False)
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    folder_description = models.CharField(max_length=300, null=True, blank=True)
    sharable = models.BooleanField(default=False, null=False)
    create_date = models.DateTimeField(auto_now_add=True, null=False)
    update_date = models.DateTimeField(auto_now=True, null=False)
    
    class Meta:
        db_table = 'share_folder'
        verbose_name = 'Share Folder'
        verbose_name_plural = 'Share Folders'
        
class ShareFile(models.Model):
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    file_name = models.CharField(max_length=100, null=False)
    folder_serial = models.ForeignKey('ShareFolder', on_delete=models.CASCADE, related_name='share_file', null=True, blank=True)
    file_serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    file_description = models.CharField(max_length=300, null=True, blank=True)
    added_to_folder = models.BooleanField(default=False, null=False)
    file_location = models.CharField(max_length=300, null=False, default='')
    file_type = models.CharField(max_length=50, null=False, default='missing file type')
    sharable = models.BooleanField(default=False, null=False)
    create_date = models.DateTimeField(auto_now_add=True, null=False)
    update_date = models.DateTimeField(auto_now=True, null=False)
    
    class Meta:
        db_table = 'share_file'
        verbose_name = 'Share File'
        verbose_name_plural = 'Share Files'
