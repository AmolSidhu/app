from django.db import models

class DataSourceUpload(models.Model):
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    serial = models.CharField(max_length=18, unique=True, primary_key=True)
    file_location = models.CharField(max_length=300)
    raw_file_location = models.CharField(max_length=300, blank=True, null=True)
    edited_file_location = models.CharField(max_length=300, blank=True, null=True)
    file_name = models.CharField(max_length=50)
    data_source_name = models.CharField(max_length=40)
    column_names = models.JSONField(default=dict)
    total_rows = models.IntegerField()
    total_columns = models.IntegerField()
    date_uploaded = models.DateTimeField(auto_now_add=True)
    data_cleaning_status = models.CharField(max_length=20, default='pending')
    data_cleaning_method_for_columns = models.JSONField(default=dict)
    data_cleaning_column_cleaning_value = models.JSONField(default=dict)
    data_cleaning_method_for_rows = models.CharField(max_length=20, default='none')
    data_cleaning_row_cleaning_value = models.IntegerField(blank=True, null=True)
    override_column_cleaning = models.BooleanField(default=False)
    
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

class DashboardItem(models.Model):
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    dashboard = models.ForeignKey('Dashboards', on_delete=models.CASCADE)
    dashboard_item_serial = models.CharField(max_length=30, primary_key=True, unique=True)
    dashboard_data_serial = models.ForeignKey('DataSourceUpload', on_delete=models.CASCADE)
    item_type = models.CharField(max_length=15)
    date_created = models.DateTimeField(auto_now_add=True)
    date_last_updated = models.DateTimeField(auto_now=True)
    item_order = models.IntegerField()
    data_item_type = models.CharField(max_length=20)
    graph_location = models.CharField(max_length=300, blank=True, null=True)
    table_location = models.CharField(max_length=300, blank=True, null=True)
    table_trunc_location = models.CharField(max_length=300, blank=True, null=True)
    table_truncated_location = models.CharField(max_length=300, blank=True, null=True)
    data_item_name = models.CharField(max_length=50)
    data_item_description = models.TextField()
    data_item_created = models.BooleanField(default=False)
    data_item_failed_creation = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'dashboard_item'
        verbose_name = 'Dashboard Item'
        verbose_name_plural = 'Dashboard Items'

class DashboardTableDataLines(models.Model):
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    dashboard_serial = models.ForeignKey('Dashboards', on_delete=models.CASCADE)
    dashboard_item_serial = models.ForeignKey('DashboardItem', on_delete=models.CASCADE)
    serial = models.CharField(max_length=30, primary_key=True, unique=True)
    column_order = models.IntegerField()
    column_name = models.CharField(max_length=50)
    source_1 = models.CharField(max_length=50, blank=True, null=True)
    source_2 = models.CharField(max_length=50, blank=True, null=True)
    operation = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        db_table = 'dashboard_table_data_lines'
        verbose_name = 'Dashboard Table Data Lines'
        verbose_name_plural = 'Dashboard Table Data Lines'

class DashboardTextData(models.Model):
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    dashboard_item_serial = models.ForeignKey('DashboardItem', on_delete=models.CASCADE)
    dashboard_serial = models.ForeignKey('Dashboards', on_delete=models.CASCADE)
    serial = models.CharField(max_length=30, primary_key=True, unique=True)
    text_header = models.CharField(max_length=100, blank=True, null=True)
    text_content = models.TextField()

    class Meta:
        db_table = 'dashboard_text_data'
        verbose_name = 'Dashboard Text Data'
        verbose_name_plural = 'Dashboard Text Data'

class DashboardGraphData(models.Model):
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    dashboard_item_serial = models.ForeignKey('DashboardItem', on_delete=models.CASCADE)
    dashboard_serial = models.ForeignKey('Dashboards', on_delete=models.CASCADE)
    serial = models.CharField(max_length=30, primary_key=True, unique=True)
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
        db_table = 'dashboard_graph_data'
        verbose_name = 'Dashboard Graph Data'
        verbose_name_plural = 'Dashboard Graph Data'


class ReportSettings(models.Model):
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    data_source = models.ForeignKey('DataSourceUpload', on_delete=models.CASCADE)
    report_serial = models.CharField(max_length=30, primary_key=True, unique=True)
    report_type = models.CharField(max_length=20)
    
    class Meta:
        db_table = 'report_settings'
        verbose_name = 'Report Settings'
        verbose_name_plural = 'Report Settings'

class ReportData(models.Model):
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE)
    report_serial = models.ForeignKey('ReportSettings', on_delete=models.CASCADE)
    serial = models.CharField(max_length=30, primary_key=True, unique=True)
    
    class Meta:
        db_table = 'report_data'
        verbose_name = 'Report Data'
        verbose_name_plural = 'Report Data'
    