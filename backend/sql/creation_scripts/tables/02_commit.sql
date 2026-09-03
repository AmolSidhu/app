BEGIN;

CREATE TABLE IF NOT EXISTS data_source_upload (
    "serial" VARCHAR(18) PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    file_location VARCHAR(300) NOT NULL,
    raw_file_location VARCHAR(300),
    edited_file_location VARCHAR(300),
    file_name VARCHAR(50) NOT NULL,
    data_source_name VARCHAR(40) NOT NULL,

    column_names JSONB NOT NULL DEFAULT '{}'::jsonb,
    data_cleaning_method_for_columns JSONB NOT NULL DEFAULT '{}'::jsonb,
    data_cleaning_column_cleaning_value JSONB NOT NULL DEFAULT '{}'::jsonb,

    total_rows INTEGER NOT NULL DEFAULT 0,
    total_columns INTEGER NOT NULL DEFAULT 0,

    date_uploaded TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    date_last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    data_cleaning_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    
    data_cleaning_method_for_columns JSONB NOT NULL DEFAULT '{}'::jsonb,
    data_cleaning_column_cleaning_value JSONB NOT NULL DEFAULT '{}'::jsonb,

    data_cleaning_method_for_rows VARCHAR(20) NOT NULL DEFAULT 'none',
    data_cleaning_row_cleaning_value INTEGER NOT NULL DEFAULT 0,

    override_column_cleaning BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS dashboards (
    user_id VARCHAR(100) NOT NULL,
    data_source_id VARCHAR(18) NOT NULL,
    dashboard_serial VARCHAR(30) PRIMARY KEY,

    dashboard_name VARCHAR(40) NOT NULL,
    dashboard_data_order JSONB NOT NULL DEFAULT '{}'::jsonb,
    date_created TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    date_last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dashboard_item (
    user_id VARCHAR(100) NOT NULL,
    dashboard_id VARCHAR(30) NOT NULL,
    data_source_id VARCHAR(18) NOT NULL,
    dashboard_item_serial VARCHAR(30) PRIMARY KEY,
    item_type VARCHAR(15) NOT NULL,
    date_created TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    date_last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    item_order INTEGER NOT NULL DEFAULT 0,
    data_item_type VARCHAR(20),
    graph_location VARCHAR(300),
    table_location VARCHAR(300),
    table_trunc_location VARCHAR(300),
    table_truncated_location VARCHAR(300),
    data_item_name VARCHAR(50),
    data_item_description TEXT,
    data_item_created BOOLEAN NOT NULL DEFAULT FALSE,
    data_item_failed_creation BOOLEAN NOT NULL DEFAULT FALSE,
    date_created TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    date_last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dashboard_table_data_lines (
    user_id VARCHAR(100) NOT NULL,
    dashboard_serial_id VARCHAR(30) NOT NULL,
    dashboard_item_serial_id VARCHAR(30) NOT NULL,
    "serial" VARCHAR(30) PRIMARY KEY,
    column_order INTEGER NOT NULL,
    column_name VARCHAR(50) NOT NULL,
    source_1 VARCHAR(50),
    source_2 VARCHAR(50),
    operation VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS dashboard_text_data (
    user_id VARCHAR(100) NOT NULL,
    dashboard_item_serial_id VARCHAR(30) NOT NULL,
    dashboard_serial_id VARCHAR(30) NOT NULL,
    "serial" VARCHAR(30) PRIMARY KEY,
    text_header VARCHAR(100),
    text_content TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dashboard_graph_data (
    user_id VARCHAR(100) NOT NULL,
    dashboard_item_serial_id VARCHAR(30) NOT NULL,
    dashboard_serial_id VARCHAR(30) NOT NULL,
    "serial" VARCHAR(30) PRIMARY KEY,

    cleaning_method VARCHAR(20) NOT NULL,
    columns JSONB NOT NULL DEFAULT '{}'::jsonb,
    x_column VARCHAR(50) NOT NULL,
    y_column VARCHAR(50) NOT NULL,
    graph_type VARCHAR(20) NOT NULL,

    edge_colour VARCHAR(20) NOT NULL DEFAULT 'black',
    line_width INTEGER NOT NULL DEFAULT 1,
    line_style VARCHAR(20) NOT NULL,
    marker_style VARCHAR(20) NOT NULL,
    marker_size INTEGER NOT NULL DEFAULT 5,
    marker_colour VARCHAR(20) NOT NULL DEFAULT 'blue',
    marker_fill VARCHAR(20) NOT NULL DEFAULT 'white',
    marker_edge VARCHAR(20) NOT NULL DEFAULT 'black',
    marker_edge_width INTEGER NOT NULL DEFAULT 1,
    marker_edge_style VARCHAR(20) NOT NULL DEFAULT 'solid',

    graph_background VARCHAR(20) NOT NULL DEFAULT 'white',
    graph_title VARCHAR(50) NOT NULL,
    graph_title_size INTEGER NOT NULL DEFAULT 16,
    graph_title_colour VARCHAR(20) NOT NULL DEFAULT 'black',

    x_axis_title VARCHAR(50) NOT NULL,
    x_axis_title_size INTEGER NOT NULL DEFAULT 14,
    x_axis_title_colour VARCHAR(20) NOT NULL DEFAULT 'black',
    x_axis_labels JSONB NOT NULL DEFAULT '{}'::jsonb,
    x_axis_label_size INTEGER NOT NULL DEFAULT 12,
    x_axis_label_colour VARCHAR(20) NOT NULL DEFAULT 'black',
    x_axis_grid BOOLEAN NOT NULL DEFAULT TRUE,

    y_axis_title VARCHAR(50) NOT NULL,
    y_axis_title_size INTEGER NOT NULL DEFAULT 14,
    y_axis_title_colour VARCHAR(20) NOT NULL DEFAULT 'black',
    y_axis_labels JSONB NOT NULL DEFAULT '{}'::jsonb,
    y_axis_label_size INTEGER NOT NULL DEFAULT 12,
    y_axis_label_colour VARCHAR(20) NOT NULL DEFAULT 'black',
    y_axis_grid BOOLEAN NOT NULL DEFAULT TRUE,

    legend_title VARCHAR(50) NOT NULL DEFAULT 'Legend',
    legend_title_size INTEGER NOT NULL DEFAULT 14,
    legend_title_colour VARCHAR(20) NOT NULL DEFAULT 'black',
    legend_labels JSONB NOT NULL DEFAULT '{}'::jsonb,
    legend_label_size INTEGER NOT NULL DEFAULT 12,
    legend_label_colour VARCHAR(20) NOT NULL DEFAULT 'black',
    legend_position VARCHAR(20) NOT NULL DEFAULT 'right',
    legend_background VARCHAR(20) NOT NULL DEFAULT 'lightgrey',
    legend_edge VARCHAR(20) NOT NULL DEFAULT 'black',
    legend_edge_width INTEGER NOT NULL DEFAULT 1,
    legend_edge_style VARCHAR(20) NOT NULL DEFAULT 'solid',

    graph_width INTEGER NOT NULL DEFAULT 800,
    graph_height INTEGER NOT NULL DEFAULT 600,
    graph_margin JSONB NOT NULL DEFAULT '{}'::jsonb,
    graph_padding JSONB NOT NULL DEFAULT '{}'::jsonb,
    graph_border JSONB NOT NULL DEFAULT '{}'::jsonb,
    graph_border_radius INTEGER NOT NULL DEFAULT 0,
    graph_border_style VARCHAR(20) NOT NULL DEFAULT 'solid',
    graph_border_width INTEGER NOT NULL DEFAULT 1,
    graph_border_colour VARCHAR(20) NOT NULL DEFAULT 'black',

    graph_shadow JSONB NOT NULL DEFAULT '{}'::jsonb,
    graph_opacity DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    antialiasing BOOLEAN NOT NULL DEFAULT TRUE,

    date_created TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    date_updated TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS report_settings (
    user_id VARCHAR(100) NOT NULL,
    data_source_id VARCHAR(18) NOT NULL,
    report_serial VARCHAR(30) PRIMARY KEY,
    report_type VARCHAR(20) NOT NULL,
    report_name VARCHAR(40) NOT NULL,
    date_created TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    date_last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS report_data (
    user_id VARCHAR(100) NOT NULL,
    report_serial_id VARCHAR(30) NOT NULL,
    "serial" VARCHAR(30) PRIMARY KEY,
);
COMMIT;