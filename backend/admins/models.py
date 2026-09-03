from django.db import models

class AdminFileRecord(models.Model):
    serial = models.CharField(max_length=100, primary_key=True, null=False)
    file_name = models.CharField(max_length=255, null=False)
    file_type = models.CharField(max_length=100, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)
    process = models.CharField(max_length=100, null=False)
    record_status = models.CharField(max_length=100, null=False)
    processed = models.BooleanField(default=False, null=False)
    file_validated = models.BooleanField(default=False, null=False)
    file_location = models.CharField(max_length=500, null=False)
    uploaded_by = models.ForeignKey('user.Credentials', on_delete=models.CASCADE, related_name='admin_file_records', null=False)
    
    class Meta:
        db_table = 'admin_file_record'
        verbose_name = 'Admin File Record'
        verbose_name_plural = 'Admin File Records'