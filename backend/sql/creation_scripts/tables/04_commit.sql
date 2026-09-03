BEGIN;

CREATE TABLE IF NOT EXISTS main_article (
    "serial" VARCHAR(18) PRIMARY KEY,
    user_id VARCHAR(18) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    created_date TIMESTAMP NOT NULL,
    last_updated_date TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS mass_upload_files (
    "serial" VARCHAR(18) PRIMARY KEY,
    user_id VARCHAR(18) NOT NULL,
    file_location VARCHAR(300) NOT NULL,
    file_extension VARCHAR(10) NOT NULL,
    file_status VARCHAR(20) NOT NULL,
    upload_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    update_date TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS json_file_uploads (
    "serial" VARCHAR(18) PRIMARY KEY,
    user_id VARCHAR(18) NOT NULL,
    file_location VARCHAR(300) NOT NULL,
    file_status VARCHAR(20) NOT NULL,
    upload_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    update_date TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS article_tags (
    "serial" VARCHAR(18) PRIMARY KEY,
    main_article_id VARCHAR(18) NOT NULL,
    tag VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS my_articles_list (
    "serial" VARCHAR(18) PRIMARY KEY,
    user_id VARCHAR(18) NOT NULL,
    my_articles_list_name VARCHAR(100) NOT NULL,
    my_articles_list_description VARCHAR(300) NOT NULL,
    create_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    update_date TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS my_articles_list_records (
    "serial" VARCHAR(18) PRIMARY KEY,
    user_id VARCHAR(18) NOT NULL,
    main_article_id VARCHAR(18) NOT NULL,
    create_date TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMIT;