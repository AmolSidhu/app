BEGIN;

ALTER TABLE admin_credentials
    ADD CONSTRAINT fk_admin_credentials_user
    FOREIGN KEY (admin_username)
    REFERENCES credentials(username)
    ON DELETE CASCADE;

COMMIT;