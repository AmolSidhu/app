BEGIN;

CREATE TABLE IF NOT EXISTS share_folder (
    user_id VARCHAR(18) NOT NULL,
    folder_name VARCHAR(100) NOT NULL,
    "serial" VARCHAR(18) PRIMARY KEY
    folder_description VARCHAR(300) NOT NULL,
    share_code VARCHAR(10) NOT NULL,
    sharable BOOLEAN NOT NULL DEFAULT FALSE,
    create_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    update_date TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS share_file (
    user_id VARCHAR(18) NOT NULL,
    file_name VARCHAR(100) NOT NULL,
    folder_serial_id VARCHAR(18) NOT NULL,
    share_code VARCHAR(100) NOT NULL,
    file_serial VARCHAR(18) PRIMARY KEY,
    file_description VARCHAR(300) NOT NULL,
    added_to_folder BOOLEAN NOT NULL DEFAULT FALSE,
    file_location VARCHAR(300) NOT NULL,
    file_type VARCHAR(20) NOT NULL,
    sharable BOOLEAN NOT NULL DEFAULT FALSE,
    create_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    update_date TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS failed_to_delete_share_file (
    file_serial VARCHAR(18) PRIMARY KEY,
    file_location VARCHAR(300) NOT NULL,
    create_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    update_date TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS failed_to_delete_share_folder (
    folder_serial VARCHAR(18) PRIMARY KEY,
    create_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    update_date TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


COMMIT;