from django.db import models

class DataSourceUpload(models.Model):
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    serial = models.CharField(max_length=18, unique=True, primary_key=True)
    file_location = models.CharField(max_length=300)
    file_name = models.CharField(max_length=50)
    data_source_name = models.CharField(max_length=40)
    column_names = models.JSONField(default=dict)
    total_rows = models.IntegerField()
    total_columns = models.IntegerField()
    date_uploaded = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'data_source_upload'
        verbose_name = 'Data Source Upload'
        verbose_name_plural = 'Data Source Uploads'

class Dashboards(models.Model):
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    data_source = models.ForeignKey('DataSourceUpload', on_delete=models.CASCADE)
    dashboard_serial = models.CharField(max_length=30, primary_key=True, unique=True)
    dashboard_name = models.CharField(max_length=40)
    dashboard_data_order = models.JSONField(default=dict)
    date_created = models.DateTimeField(auto_now_add=True)
    date_last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dashboards'
        verbose_name = 'Dashboard'
        verbose_name_plural = 'Dashboards'

class DashboardData(models.Model):
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    dashboard = models.ForeignKey('Dashboards', on_delete=models.CASCADE)
    dashboard_data_serial = models.CharField(max_length=30, primary_key=True, unique=True)
    data_order = models.IntegerField()
    data_type = models.CharField(max_length=15)
    data_location = models.CharField(max_length=300)
    
    class Meta:
        db_table = 'dashboard_data'
        verbose_name = 'Dashboard Data'
        verbose_name_plural = 'Dashboard Data'

class DashboardItem(models.Model):
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    dashboard = models.ForeignKey('Dashboards', on_delete=models.CASCADE)
    dashboard_item_serial = models.CharField(max_length=30, primary_key=True, unique=True)
    dashboard_data_serial = models.ForeignKey('DashboardData', on_delete=models.CASCADE)
    item_description = models.TextField()
    item_graph_type = models.CharField(max_length=20)
    item_graph_style = models.JSONField(default=dict)
    item_graph_data_agg = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'dashboard_item'
        verbose_name = 'Dashboard Item'
        verbose_name_plural = 'Dashboard Items'
    