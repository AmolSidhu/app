{% autoescape off %}
BEGIN;

CREATE SCHEMA IF NOT EXISTS {{ schema }};
COMMENT ON SCHEMA {{ schema }} IS {{ comment }};
ALTER SCHEMA {{ schema }} OWNER TO {{ owner }};

COMMIT;
{% endautoescape %}
