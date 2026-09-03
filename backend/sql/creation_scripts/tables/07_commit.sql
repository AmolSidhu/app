BEGIN;

ALTER TABLE share_folder 
    ADD CONSTRAINT fk_share_folder_user
    FOREIGN KEY (user_id)
    REFERENCES credentials(username)
    ON DELETE CASCADE;

ALTER TABLE share_file
    ADD CONSTRAINT fk_share_file_user
    FOREIGN KEY (user_id)
    REFERENCES credentials(username)
    ON DELETE CASCADE;

ALTER TABLE share_file
    ADD CONSTRAINT fk_share_file_folder
    FOREIGN KEY (folder_serial_id)
    REFERENCES share_folder("serial")
    ON DELETE CASCADE;

COMMIT;