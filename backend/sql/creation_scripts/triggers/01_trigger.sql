
-- Trigger and Function to update last_updated column in credentials table on update

BEGIN;

CREATE OR REPLACE FUNCTION update_credentials_last_updated()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_credentials_last_updated
BEFORE UPDATE ON credentials
FOR EACH ROW
EXECUTE FUNCTION update_credentials_last_updated();

COMMIT;