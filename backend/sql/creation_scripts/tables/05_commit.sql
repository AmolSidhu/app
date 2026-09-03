BEGIN;

ALTER TABLE main_article
    ADD CONSTRAINT fk_main_article_user
    FOREIGN KEY (user_id)
    REFERENCES credentials(username)
    ON DELETE CASCADE;

ALTER TABLE mass_upload_files
    ADD CONSTRAINT fk_mass_upload_files_user
    FOREIGN KEY (user_id)
    REFERENCES credentials(username)
    ON DELETE CASCADE;

ALTER TABLE json_file_uploads
    ADD CONSTRAINT fk_json_file_uploads_user
    FOREIGN KEY (user_id)
    REFERENCES credentials(username)
    ON DELETE CASCADE;

ALTER TABLE article_tags
    ADD CONSTRAINT fk_article_tags_main_article
    FOREIGN KEY (main_article_id)
    REFERENCES main_article("serial")
    ON DELETE CASCADE;

ALTER TABLE my_articles_list
    ADD CONSTRAINT fk_my_articles_list_user
    FOREIGN KEY (user_id)
    REFERENCES credentials(username)
    ON DELETE CASCADE;

ALTER TABLE my_articles_list_records
    ADD CONSTRAINT fk_my_articles_list_records_user
    FOREIGN KEY (user_id)
    REFERENCES credentials(username)
    ON DELETE CASCADE;

ALTER TABLE my_articles_list_records
    ADD CONSTRAINT fk_my_articles_list_records_main_article
    FOREIGN KEY (main_article_id)
    REFERENCES main_article("serial")
    ON DELETE CASCADE;

COMMIT;