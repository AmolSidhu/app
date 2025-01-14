from django.db import models

class Identifier(models.Model):
    identifier = models.CharField(max_length=12, unique=True, primary_key=True, null=False)
    current_status = models.CharField(max_length=100, null=True)
    created = models.DateTimeField(auto_now_add=True, null=False)
    last_updated = models.DateTimeField(auto_now=True, null=False)
    title = models.CharField(max_length=100, null=True)
    json_location = models.CharField(max_length=300, null=True)
    
    class Meta:
        db_table = 'identifiers'
        verbose_name = 'Identifier'
        verbose_name_plural = 'Identifiers'
    
class IdentifierTempTable(models.Model):
    temp_name = models.CharField(max_length=100, unique=True, primary_key=True, null=False)
    file_location = models.CharField(max_length=300, null=False)
    add_status = models.BooleanField(default=False, null=False)
    
    class Meta:
        db_table = 'identifiers_temp_table'
        verbose_name = 'Identifier Temp Table'
        verbose_name_plural = 'Identifier Temp Tables'

class TempGenreTable(models.Model):
    genre = models.CharField(max_length=100, unique=True, primary_key=True, null=False)
    number_of_public_records = models.IntegerField(default=0, null=False)
    custom = models.BooleanField(default=False, null=False)
    
    def __str__(self):
        return f"Genre: {self.genre}, Number of Public Records: {self.number_of_public_records}, Custom: {self.custom}"
        
    class Meta:
        db_table = 'genre_temp_table'
        verbose_name = 'Genre Temp Table'
        verbose_name_plural = 'Genre Temp Tables'
        
        
class FailedDeletionRecords(models.Model):
    file_path = models.CharField(max_length=300, null=False)
    delete_status = models.BooleanField(default=True, null=False)
    
    class Meta:
        db_table = 'failed_deletion_records'
        verbose_name = 'Failed Deletion Record'
        verbose_name_plural = 'Failed Deletion Records'