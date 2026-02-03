import os
import pandas as pd

def create_table(
    data_location,
    serial,
    source_1_columns=None,
    source_2_columns=None,
    operations=None,
    save_path=None,
    column_names=None,
    data_source_serial=None,
    data_sample_path=None
):
    try:
        full_path = os.path.join(data_location, f"{data_source_serial}.csv")
        if not os.path.exists(full_path):
            print(f"File {full_path} does not exist.")
            return False

        source_1_columns = source_1_columns or []
        source_2_columns = source_2_columns or []
        operations = operations or []
        column_names = column_names or []

        columns = []

        for col in source_1_columns:
            if col and col != "empty_source_2" and col not in columns:
                columns.append(col)

        for col in source_2_columns:
            if col and col != "empty_source_2" and col not in columns:
                columns.append(col)

        df = pd.read_csv(full_path, usecols=columns)

        table_data = pd.DataFrame(index=df.index)

        for i in range(len(source_1_columns)):
            col1 = source_1_columns[i]
            col2 = source_2_columns[i] if i < len(source_2_columns) else None
            op = operations[i] if i < len(operations) else "empty_operation"

            col_name = (
                column_names[i]
                if i < len(column_names) and column_names[i]
                else f"Column_{i + 1}"
            )

            if not col1:
                table_data[col_name] = None
                continue

            if col1 not in df.columns:
                table_data[col_name] = None
                continue

            if (
                op != "empty_operation"
                and col2
                and col2 in df.columns
            ):
                if op == "add":
                    table_data[col_name] = (df[col1] + df[col2]).round(2)
                elif op == "subtract":
                    table_data[col_name] = (df[col1] - df[col2]).round(2)
                elif op == "multiply":
                    table_data[col_name] = (df[col1] * df[col2]).round(2)
                elif op == "divide":
                    table_data[col_name] = (df[col1] / df[col2]).round(2)
                else:
                    table_data[col_name] = None

            else:
                table_data[col_name] = df[col1].round(2)

        save_path = os.path.join(save_path, f"{serial}.html")

        if len(table_data) > 10 and data_sample_path:
            sample_df = pd.concat([table_data.head(5), table_data.tail(5)])
            sample_path = os.path.join(data_sample_path, f"{serial}.html")
            sample_df.to_html(sample_path, index=False)

        table_data.to_html(save_path, index=False)

        return True

    except Exception as e:
        print(f"Error creating table: {e}")
        return False
