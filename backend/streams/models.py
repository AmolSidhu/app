from django.db import models

class TempStreamData(models.Model):
    serial = models.CharField(max_length=100, primary_key=True, unique=True, null=False)
    user =models.ForeignKey('user.Credentials', on_delete=models.CASCADE, null=False)
    stream_text = models.TextField(null=False)
    stream_data = models.JSONField(null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)