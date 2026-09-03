BEGIN;

CREATE TABLE IF NOT EXISTS credentials (
    username VARCHAR(100) PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    "password" VARCHAR(100) NOT NULL,
    verification_code VARCHAR(100) NOT NULL DEFAULT '',
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,

    first_name VARCHAR(100) NOT NULL DEFAULT '',
    last_name VARCHAR(100) NOT NULL DEFAULT '',

    permission INTEGER NOT NULL DEFAULT 2,
    user_status VARCHAR(100) NOT NULL DEFAULT 'Active',

    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,

    date_joined TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_status_updated_date TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS admin_credentials (
    admin_code VARCHAR(100) PRIMARY KEY,
    admin_username VARCHAR(100) NOT NULL,
    admin_email VARCHAR(100) NOT NULL,
    active_admin BOOLEAN NOT NULL DEFAULT FALSE
);

COMMIT;