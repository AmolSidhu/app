from django.db import models

class ScraperUploadFile(models.Model):
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    file_name = models.CharField(max_length=100, null=False)
    scraper_name = models.CharField(max_length=100, null=False)
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    scraper_description = models.CharField(max_length=300, null=True, blank=True)
    file_location = models.CharField(max_length=300, null=False, default='')
    status = models.CharField(max_length=50, null=False, default='validating')
    file_type = models.CharField(max_length=50, null=False, default='missing file type')
    create_date = models.DateTimeField(auto_now_add=True, null=False)
    update_date = models.DateTimeField(auto_now=True, null=False)

    class Meta:
        db_table = 'scraper_upload_file'
        verbose_name = 'Scraper Upload File'
        verbose_name_plural = 'Scraper Upload Files'
        
class ScraperOutputFile(models.Model):
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    file_name = models.CharField(max_length=100, null=False)
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    scraper_file = models.ForeignKey('ScraperUploadFile', on_delete=models.CASCADE, related_name='scraper_output_file', null=False)
    run_number = models.IntegerField(null=False, default=1)
    status = models.CharField(max_length=50, null=False, default='processing')
    file_location = models.CharField(max_length=300, null=False, default='')
    create_date = models.DateTimeField(auto_now_add=True, null=False)
    update_date = models.DateTimeField(auto_now=True, null=False)

    class Meta:
        db_table = 'scraper_output_file'
        verbose_name = 'Scraper Output File'
        verbose_name_plural = 'Scraper Output Files'