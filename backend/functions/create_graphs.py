import pandas as pd
import os
import json
import seaborn as sns
import matplotlib.pyplot as plt

def create_graph(graph_type, data_location, dashboard_serial, dashboard_data_serial,
                 graph_settings_serial, user, cleaning_method, columns, graph_complexity):
    dataframe = create_dataframe(data_location, columns)
    data = dataframe['data']
    cleaned_data = clean_data(data, cleaning_method, columns)
    if graph_complexity == 'basic':
        graph = create_basic_graph(graph_type, cleaned_data)
    elif graph_complexity == 'advanced':
        graph = create_advanced_graph(graph_type, cleaned_data)
    else:
        return None
    save_graph(graph, dashboard_serial, dashboard_data_serial, graph_settings_serial, user)
    
    return 'Graph created successfully'

def clean_data(data, cleaning_method, columns):
    if cleaning_method == 'drop_duplicates':
        cleaned_data = data.drop_duplicates()
    elif cleaning_method == 'dropna':
        cleaned_data = data.dropna()
    elif cleaning_method == 'fillna':
        cleaned_data = data.fillna(0)
    elif cleaning_method == 'replace':
        cleaned_data = data.replace('?', 0)
    elif cleaning_method == 'drop_columns':
        cleaned_data = data.drop(columns, axis=1)
    return {'data': cleaned_data}

def create_dataframe(data_location, columns):
    data = pd.read_csv(data_location, usecols=columns)
    return {'data': data}

def get_graph_settings(graph_settings_serial):
    return None

def save_graph():
    return None

def create_basic_graph():
    return None

def create_advanced_graph():
    return None

def create_basic_pie_chart():
    return None

def create_advanced_pie_chart():
    return None

def create_basic_bar_chart():
    return None

def create_advanced_bar_chart():
    return None

def create_basic_line_chart():
    return None

def create_advanced_line_chart():
    return None

def create_basic_scatter_plot():
    return None

def create_advanced_scatter_plot():
    return None

def create_basic_heatmap():
    return None

def create_advanced_heatmap():
    return None

def create_basic_box_plot():
    return None

def create_advanced_box_plot():
    return None

def create_basic_violin_plot():
    return None

def create_advanced_violin_plot():
    return None
