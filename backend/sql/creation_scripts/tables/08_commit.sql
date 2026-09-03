BEGIN;

CREATE TABLE IF NOT EXISTS identifiers (
    identifier VARCHAR(12) PRIMARY KEY,
    current_status VARCHAR(20) NOT NULL,
    create_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    title VARCHAR(100),
    json_location VARCHAR(300),
    rerun_status BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS identifiers_temp_table (
    temp_name VARCHAR(30) PRIMARY KEY,
    file_location VARCHAR(300) NOT NULL,
    add_status BOOLEAN NOT NULL DEFAULT FALSE,
);

CREATE TABLE IF NOT EXISTS genre_temp_table (
    genre VARCHAR(100) PRIMARY KEY,
    number_of_public_records INTEGER NOT NULL DEFAULT 0,
    custom BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS failed_deletion_records (
    "serial" VARCHAR(30) PRIMARY KEY,
    source VARCHAR(30) NOT NULL,
    file_path VARCHAR(300) NOT NULL,
    delete_status BOOLEAN NOT NULL DEFAULT FALSE
);

COMMIT;