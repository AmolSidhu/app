from django.db import models
from django.contrib.auth.models import AbstractUser

class Credentials(AbstractUser):
    email = models.EmailField(unique=True, max_length=100, null=False)
    username = models.CharField(max_length=100, unique=True, primary_key=True, null=False)
    password = models.CharField(max_length=100, null=False)
    verification_code = models.CharField(max_length=100, default='', null=False)
    is_verified = models.BooleanField(default=False, null=False)
    date_joined = models.DateTimeField(auto_now_add=True, null=False)
    last_updated = models.DateTimeField(auto_now=True, null=False)
    last_login = models.DateTimeField(auto_now=True, null=False)
    permission = models.IntegerField(default=2, null=False)
    first_name = models.CharField(max_length=100, default='', null=False)
    last_name = models.CharField(max_length=100, default='', null=False)
    user_status = models.CharField(max_length=100, default='Active', null=False)
    user_status_updated_date = models.DateTimeField(auto_now=True, null=False)
    is_active = models.BooleanField(default=True, null=False)
    is_staff = models.BooleanField(default=False, null=False)
    is_superuser = models.BooleanField(default=False, null=False)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'password']
    
    class Meta:
        db_table = 'credentials'
        verbose_name = 'Credentials'
        verbose_name_plural = 'Credentials' 

class AdminCredentials(models.Model):
    admin_username = models.ForeignKey(Credentials, on_delete=models.CASCADE, related_name='admin_credentials', null=False)
    admin_email = models.CharField(max_length=100, null=False)
    admin_code = models.CharField(max_length=100, default='', null=False, primary_key=True)
    active_admin = models.BooleanField(default=False, null=False)
    
    class Meta:
        db_table = 'admin_credentials'
        verbose_name = 'AdminCredentials'
        verbose_name_plural = 'AdminCredentials'