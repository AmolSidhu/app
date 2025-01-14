from django.db import models

class DataSourceUpload(models.Model):
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    serial = models.CharField(max_length=12)
    file_location = models.CharField(max_length=300)
    file_name = models.CharField(max_length=50)
    column_names = models.JSONField(default=dict)

class Dashboards(models.Model):
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    data_source = models.ForeignKey('DataSourceUpload', on_delete=models.CASCADE)
    dashboard_name = models.CharField(max_length=40)
    dashboard_data_order = models.JSONField(default=dict)

class DashboardData(models.Model):
    dashboard = models.ForeignKey('Dashboards', on_delete=models.CASCADE)
    dhasboard_serial = models.CharField(max_length=100)
    data_order = models.IntegerField()
    data_type = models.CharField(max_length=15)
    