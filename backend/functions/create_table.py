import os
import pandas as pd

def create_table(data_location, serial, source_1_columns=None, source_2_columns=None,
                 operations=None, save_path=None, column_names=None, data_source_serial=None,
                 data_sample_path=None):
    try:
        full_path = os.path.join(data_location, data_source_serial + '.csv')
        if not os.path.exists(full_path):
            print(f"File {full_path} does not exist.")
            return None

        columns = []
        if source_1_columns:
            for column in source_1_columns:
                if column and column != 'empty_source_2' and column not in columns:
                    columns.append(column)
        if source_2_columns:
            for column in source_2_columns:
                if column and column != 'empty_source_2' and column not in columns:
                    columns.append(column)

        df = pd.read_csv(full_path, usecols=columns)

        table_data = pd.DataFrame()

        for i in range(len(source_1_columns)):
            col1 = source_1_columns[i]
            col2 = source_2_columns[i]
            op = operations[i]
            col_name = column_names[i]

            if col1 in df.columns:
                if op != 'empty_operation':
                    if op == 'add':
                        table_data[col_name] = (df[col1] + df[col2]).round(2)
                    elif op == 'subtract':
                        table_data[col_name] = (df[col1] - df[col2]).round(2)
                    elif op == 'multiply':
                        table_data[col_name] = (df[col1] * df[col2]).round(2)
                    elif op == 'divide':
                        table_data[col_name] = (df[col1] / df[col2]).round(2)
                else:
                    table_data[col_name] = df[col1].round(2)

        save_path = os.path.join(save_path, serial + '.html')
        
        total_df_lines = len(table_data)
        if total_df_lines <= 10:
            pass
        else:
            data_sample = pd.concat([table_data.head(5), table_data.tail(5)])
            sample_path = os.path.join(data_sample_path, serial + '.html')
            data_sample.to_html(sample_path, index=False)

        table_data.to_html(save_path, index=False)
        print(f"Table saved to {save_path}")

        return True
    except Exception as e:
        print(f"Error creating table: {e}")
        return False
