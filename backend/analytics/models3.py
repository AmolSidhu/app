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

#### Unused Table ####
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
    dashboard_data_serial = models.ForeignKey('DataSourceUpload', on_delete=models.CASCADE)
    item_type = models.CharField(max_length=15)
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
    serial = models.CharField(max_length=30, primary_key=True, unique=True)
    dashboard_item_serial = models.ForeignKey('DashboardItem', on_delete=models.CASCADE)
    dashboard_item_data_serial = models.ForeignKey('DashboardItemData', on_delete=models.CASCADE)
    dashboard_serial = models.ForeignKey('Dashboards', on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    table_created = models.BooleanField(default=False)
    table_failed = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'dashboard_item_table'
        verbose_name = 'Dashboard Item Table'
        verbose_name_plural = 'Dashboard Item Tables'

class DashboardItemTableLines(models.Model):
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    serial = models.CharField(max_length=30, primary_key=True, unique=True)
    dashboard_item_table_serial = models.ForeignKey('DashboardItemTable', on_delete=models.CASCADE)
    dashboard_table_serial = models.ForeignKey('DashboardItem', on_delete=models.CASCADE)
    dashboard_serial = models.ForeignKey('Dashboards', on_delete=models.CASCADE)
    column_order = models.IntegerField()
    column_name = models.CharField(max_length=50)
    source_1 = models.CharField(max_length=50)
    source_2 = models.CharField(max_length=50)
    operation = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'dashboard_item_table_lines'
        verbose_name = 'Dashboard Item Table Lines'
        verbose_name_plural = 'Dashboard Item Table Lines'

class DashboardItemGraph(models.Model):
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    serial = models.CharField(max_length=30, primary_key=True, unique=True)
    dashboard_item_serial = models.ForeignKey('DashboardItem', on_delete=models.CASCADE)
    dashboard_item_data_serial = models.ForeignKey('DashboardItemData', on_delete=models.CASCADE)
    dashboard_serial = models.ForeignKey('Dashboards', on_delete=models.CASCADE)
    graph_location = models.CharField(max_length=300)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    graph_created = models.BooleanField(default=False)
    graph_failed = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'dashboard_item_graph'
        verbose_name = 'Dashboard Item Graph'
        verbose_name_plural = 'Dashboard Item Graphs'

class DashboardItemText(models.Model):
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    serial = models.CharField(max_length=30, primary_key=True, unique=True)
    dashboard_item_serial = models.ForeignKey('DashboardItem', on_delete=models.CASCADE)
    dashboard_item_data_serial = models.ForeignKey('DashboardItemData', on_delete=models.CASCADE)
    dashboard_serial = models.ForeignKey('Dashboards', on_delete=models.CASCADE)
    text_header = models.CharField(max_length=50)
    text_body = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dashboard_item_text'
        verbose_name = 'Dashboard Item Text'
        verbose_name_plural = 'Dashboard Item Texts'
    
class GraphSettings(models.Model):
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    dashboard = models.ForeignKey('Dashboards', on_delete=models.CASCADE)
    dashboard_item = models.ForeignKey('DashboardItem', on_delete=models.CASCADE)
    dashboard_item_graph = models.ForeignKey('DashboardItemGraph', on_delete=models.CASCADE)
    graph_settings_serial = models.CharField(max_length=30, primary_key=True, unique=True)
    cleaning_method = models.CharField(max_length=20)
    columns = models.JSONField(default=dict)
    x_column = models.CharField(max_length=50)
    y_column = models.CharField(max_length=50)
    graph_type = models.CharField(max_length=20)
    edge_colour = models.CharField(max_length=20, default='black')
    line_width = models.IntegerField(default=1)
    line_style = models.CharField(max_length=20)
    marker_style = models.CharField(max_length=20)
    marker_size = models.IntegerField(default=5)
    marker_colour = models.CharField(max_length=20, default='blue')
    marker_fill = models.CharField(max_length=20, default='white')
    marker_edge = models.CharField(max_length=20, default='black')
    marker_edge_width = models.IntegerField(default=1)
    marker_edge_style = models.CharField(max_length=20, default='solid')
    graph_background = models.CharField(max_length=20, default='white')
    graph_title = models.CharField(max_length=50)
    graph_title_size = models.IntegerField(default=16)
    graph_title_colour = models.CharField(max_length=20, default='black')
    x_axis_title = models.CharField(max_length=50)
    x_axis_title_size = models.IntegerField(default=14)
    x_axis_title_colour = models.CharField(max_length=20, default='black')
    x_axis_labels = models.JSONField(default=dict)
    x_axis_label_size = models.IntegerField(default=12)
    x_axis_label_colour = models.CharField(max_length=20, default='black')
    x_axis_grid = models.BooleanField(default=True) 
    y_axis_title = models.CharField(max_length=50)
    y_axis_title_size = models.IntegerField(default=14)
    y_axis_title_colour = models.CharField(max_length=20, default='black')
    y_axis_labels = models.JSONField(default=dict)
    y_axis_label_size = models.IntegerField(default=12)
    y_axis_label_colour = models.CharField(max_length=20, default='black')
    y_axis_grid = models.BooleanField(default=True)
    legend_title = models.CharField(max_length=50, default='Legend')
    legend_title_size = models.IntegerField(default=14)
    legend_title_colour = models.CharField(max_length=20, default='black')
    legend_labels = models.JSONField(default=dict)
    legend_label_size = models.IntegerField(default=12)
    legend_label_colour = models.CharField(max_length=20, default='black')
    legend_position = models.CharField(max_length=20, default='right')
    legend_background = models.CharField(max_length=20, default='lightgrey')
    legend_edge = models.CharField(max_length=20, default='black')
    legend_edge_width = models.IntegerField(default=1)
    legend_edge_style = models.CharField(max_length=20, default='solid')
    graph_width = models.IntegerField(default=800)
    graph_height = models.IntegerField(default=600)
    graph_margin = models.JSONField(default=dict)
    graph_padding = models.JSONField(default=dict)
    graph_border = models.JSONField(default=dict)
    graph_border_radius = models.IntegerField(default=0)
    graph_border_style = models.CharField(max_length=20, default='solid')
    graph_border_width = models.IntegerField(default=1)
    graph_border_colour = models.CharField(max_length=20, default='black')
    graph_shadow = models.JSONField(default=dict)
    graph_opacity = models.FloatField(default=1.0)
    antialiasing = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)    
    
    class Meta:
        db_table = 'graph_settings'
        verbose_name = 'Graph Settings'
        verbose_name_plural = 'Graph Settings'