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
    item_type = models.CharField(max_length=15),
    date_created = models.DateTimeField(auto_now_add=True)
    date_last_updated = models.DateTimeField(auto_now=True)
    item_order = models.IntegerField()
    
    class Meta:
        db_table = 'dashboard_item'
        verbose_name = 'Dashboard Item'
        verbose_name_plural = 'Dashboard Items'
        
class DashboardItemData(models.Model):
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    serial = models.CharField(max_length=30, primary_key=True, unique=True)
    dashboard_item = models.ForeignKey('DashboardItem', on_delete=models.CASCADE)
    data_item_type = models.CharField(max_length=20)
    data_item_location = models.CharField(max_length=300)
    data_item_name = models.CharField(max_length=50)
    data_item_description = models.TextField()
    
    class Meta:
        db_table = 'dashboard_item_data'
        verbose_name = 'Dashboard Item Data'
        verbose_name_plural = 'Dashboard Item Data'

class DashboardItemTable(models.Model):
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'dashboard_item_table'
        verbose_name = 'Dashboard Item Table'
        verbose_name_plural = 'Dashboard Item Tables'

class DashboardItemGraph(models.Model):
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'dashboard_item_graph'
        verbose_name = 'Dashboard Item Graph'
        verbose_name_plural = 'Dashboard Item Graphs'
    
class DashboardItemText(models.Model):
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'dashboard_item_text'
        verbose_name = 'Dashboard Item Text'
        verbose_name_plural = 'Dashboard Item Texts'
    
class GraphSettings(models.Model):
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    dashboard = models.ForeignKey('Dashboards', on_delete=models.CASCADE)
    dashboard_item = models.ForeignKey('DashboardItem', on_delete=models.CASCADE)
    graph_settings_serial = models.CharField(max_length=30, primary_key=True, unique=True)
    graph_type = models.CharField(max_length=20)
    edge_colour = models.CharField(max_length=20)
    line_width = models.IntegerField()
    line_style = models.CharField(max_length=20)
    marker_style = models.CharField(max_length=20)
    marker_size = models.IntegerField()
    marker_colour = models.CharField(max_length=20)
    marker_fill = models.CharField(max_length=20)
    marker_edge = models.CharField(max_length=20)
    marker_edge_width = models.IntegerField()
    marker_edge_style = models.CharField(max_length=20)
    graph_background = models.CharField(max_length=20)
    graph_title = models.CharField(max_length=50)
    graph_title_size = models.IntegerField()
    graph_title_colour = models.CharField(max_length=20)
    x_axis_title = models.CharField(max_length=50)
    x_axis_title_size = models.IntegerField()
    x_axis_title_colour = models.CharField(max_length=20)
    x_axis_labels = models.JSONField(default=dict)
    x_axis_label_size = models.IntegerField()
    x_axis_label_colour = models.CharField(max_length=20)
    x_axis_grid = models.BooleanField() 
    y_axis_title = models.CharField(max_length=50)
    y_axis_title_size = models.IntegerField()
    y_axis_title_colour = models.CharField(max_length=20)
    y_axis_labels = models.JSONField(default=dict)
    y_axis_label_size = models.IntegerField()
    y_axis_label_colour = models.CharField(max_length=20)
    y_axis_grid = models.BooleanField()
    legend_title = models.CharField(max_length=50)
    legend_title_size = models.IntegerField()
    legend_title_colour = models.CharField(max_length=20)
    legend_labels = models.JSONField(default=dict)
    legend_label_size = models.IntegerField()
    legend_label_colour = models.CharField(max_length=20)
    legend_position = models.CharField(max_length=20)
    legend_background = models.CharField(max_length=20)
    legend_edge = models.CharField(max_length=20)
    legend_edge_width = models.IntegerField()
    legend_edge_style = models.CharField(max_length=20)
    graph_width = models.IntegerField()
    graph_height = models.IntegerField()
    graph_margin = models.JSONField(default=dict)
    graph_padding = models.JSONField(default=dict)
    graph_border = models.JSONField(default=dict)
    graph_border_radius = models.IntegerField()
    graph_border_style = models.CharField(max_length=20)
    graph_border_width = models.IntegerField()
    graph_border_colour = models.CharField(max_length=20)
    graph_shadow = models.JSONField(default=dict)
    graph_opacity = models.FloatField()
    antialiasing = models.BooleanField()
    
    class Meta:
        db_table = 'graph_settings'
        verbose_name = 'Graph Settings'
        verbose_name_plural = 'Graph Settings'