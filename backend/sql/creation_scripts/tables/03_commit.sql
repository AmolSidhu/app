BEGIN;

ALTER TABLE data_source_upload
    ADD CONSTRAINT fk_data_source_upload_user
    FOREIGN KEY (user_id)
    REFERENCES credentials(username)
    ON DELETE CASCADE;

ALTER TABLE dashboards
    ADD CONSTRAINT fk_dashboards_user
    FOREIGN KEY (user_id)
    REFERENCES credentials(username)
    ON DELETE CASCADE;

ALTER TABLE dashboards
    ADD CONSTRAINT fk_dashboards_data_source_upload
    FOREIGN KEY (data_source_id)
    REFERENCES data_source_upload("serial")
    ON DELETE CASCADE;

ALTER TABLE dashboard_item
    ADD CONSTRAINT fk_dashboard_item_user
    FOREIGN KEY (user_id)
    REFERENCES credentials(username)
    ON DELETE CASCADE;

ALTER TABLE dashboard_item
    ADD CONSTRAINT fk_dashboard_item_dashboards
    FOREIGN KEY (dashboard_id)
    REFERENCES dashboards(dashboard_serial)
    ON DELETE CASCADE;

ALTER TABLE dashboard_item
    ADD CONSTRAINT fk_dashboard_item_data_source_upload
    FOREIGN KEY (data_source_id)
    REFERENCES data_source_upload("serial")
    ON DELETE CASCADE;

ALTER TABLE dashboard_table_data_lines
    ADD CONSTRAINT fk_dashboard_table_data_lines_user
    FOREIGN KEY (user_id)
    REFERENCES credentials(username)
    ON DELETE CASCADE;

ALTER TABLE dashboard_table_data_lines
    ADD CONSTRAINT fk_dashboard_table_data_lines_dashboard
    FOREIGN KEY (dashboard_serial_id)
    REFERENCES dashboards(dashboard_serial)
    ON DELETE CASCADE;

ALTER TABLE dashboard_table_data_lines
    ADD CONSTRAINT fk_dashboard_table_data_lines_dashboard_item
    FOREIGN KEY (dashboard_item_serial_id)
    REFERENCES dashboard_item(dashboard_item_serial)
    ON DELETE CASCADE;

ALTER TABLE dashboard_text_data
    ADD CONSTRAINT fk_dashboard_text_data_user
    FOREIGN KEY (user_id)
    REFERENCES credentials(username)
    ON DELETE CASCADE;

ALTER TABLE dashboard_text_data
    ADD CONSTRAINT fk_dashboard_text_data_dashboard_item
    FOREIGN KEY (dashboard_item_serial_id)
    REFERENCES dashboard_item(dashboard_item_serial)
    ON DELETE CASCADE;

ALTER TABLE dashboard_text_data
    ADD CONSTRAINT fk_dashboard_text_data_dashboard
    FOREIGN KEY (dashboard_serial_id)
    REFERENCES dashboards(dashboard_serial)
    ON DELETE CASCADE;

ALTER TABLE dashboard_graph_data
    ADD CONSTRAINT fk_dashboard_graph_data_user
    FOREIGN KEY (user_id)
    REFERENCES credentials(username)
    ON DELETE CASCADE;

ALTER TABLE dashboard_graph_data
    ADD CONSTRAINT fk_dashboard_graph_data_dashboard_item
    FOREIGN KEY (dashboard_item_serial_id)
    REFERENCES dashboard_item(dashboard_item_serial)
    ON DELETE CASCADE;

ALTER TABLE dashboard_graph_data
    ADD CONSTRAINT fk_dashboard_graph_data_dashboard
    FOREIGN KEY (dashboard_serial_id)
    REFERENCES dashboards(dashboard_serial)
    ON DELETE CASCADE;

ALTER TABLE report_settings
    ADD CONSTRAINT fk_report_settings_user
    FOREIGN KEY (user_id)
    REFERENCES credentials(username)
    ON DELETE CASCADE;

ALTER TABLE report_settings
    ADD CONSTRAINT fk_report_settings_data_source_upload
    FOREIGN KEY (data_source_id)
    REFERENCES data_source_upload("serial")
    ON DELETE CASCADE;

ALTER TABLE report_data
    ADD CONSTRAINT fk_report_data_user
    FOREIGN KEY (user_id)
    REFERENCES credentials(username)
    ON DELETE CASCADE;

ALTER TABLE report_data
    ADD CONSTRAINT fk_report_data_report_settings
    FOREIGN KEY (report_serial_id)
    REFERENCES report_settings(report_serial)
    ON DELETE CASCADE;
COMMIT;