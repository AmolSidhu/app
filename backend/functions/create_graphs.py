import pandas as pd
import os
import json
import seaborn as sns

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def generate_basic_graph(graph_type, data_location, cleaning_method, columns,
                         column_1=None, column_2=None, graph_title=None,
                         save_path=None, serial=None, x_label=None,
                         y_label=None, data_source_serial=None):
    
    try:
        data_file = os.path.join(data_location, f"{data_source_serial}.csv")
        data = pd.read_csv(data_file, usecols=columns)

        if cleaning_method == 'drop_duplicates':
            data = data.drop_duplicates()
        elif cleaning_method == 'dropna':
            data = data.dropna()
        elif cleaning_method == 'fillna':
            data = data.fillna(0)
        elif cleaning_method == 'replace':
            data = data.replace('?', 0)
        elif cleaning_method == 'drop_columns':
            data = data.drop(columns, axis=1)
        elif cleaning_method == 'drop_rows':
            data = data.drop(data.index[0:5])

        plt.figure(figsize=(10, 6))
        plt.title(graph_title if graph_title else f'{graph_type.capitalize()} Graph')

        if column_1:
            plt.xlabel(x_label)
        if column_2:
            plt.ylabel(y_label)

        if graph_type == 'pie':
            data[column_1].value_counts().plot.pie(autopct='%1.1f%%')
            plt.ylabel('')

        elif graph_type == 'bar':
            if column_2:
                sns.barplot(x=column_1, y=column_2, data=data)
            else:
                data[column_1].value_counts().plot(kind='bar')

        elif graph_type == 'line':
            if column_2:
                plt.plot(data[column_1], data[column_2])
            else:
                plt.plot(data[column_1])

        elif graph_type == 'scatter':
            if column_2:
                plt.scatter(data[column_1], data[column_2])
            else:
                print("Error: Scatter plot requires two columns.")
                return

        elif graph_type == 'heatmap':
            sns.heatmap(data.corr(), annot=True, cmap='coolwarm')

        elif graph_type == 'boxplot':
            if column_2:
                sns.boxplot(x=column_1, y=column_2, data=data)
            else:
                sns.boxplot(y=data[column_1])

        elif graph_type == 'violin':
            if column_2:
                sns.violinplot(x=column_1, y=column_2, data=data)
            else:
                sns.violinplot(y=data[column_1])

        else:
            print("Error: Unsupported graph type.")
            return

        plt.tight_layout()
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        file_path = os.path.join(os.path.dirname(save_path), f"{serial}.png")
        plt.savefig(file_path, format='png')
        plt.close()
        print(f"Graph saved to {save_path}")
        
        return True
    except Exception as e:
        print(f"Error generating graph: {e}")
        return False


def create_advanced_graph(graph_type):
    if graph_type == 'pie':
        pass
    if graph_type == 'bar':
        pass
    if graph_type == 'line':
        pass
    if graph_type == 'scatter':
        pass
    if graph_type == 'heatmap':
        pass
    if graph_type == 'box':
        pass
    if graph_type == 'violin':
        pass