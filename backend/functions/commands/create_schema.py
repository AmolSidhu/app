from django.db import connection, transaction
from django.template import engines
from psycopg import sql

def create_schema():
    owner = input("Enter schema owner: ").strip()
    schema = input("Enter schema name: ").strip()
    comment = input("Enter schema comment: ").strip()

    sql_path = "sql/creation_scripts/scripts/create.sql"

    with open(sql_path) as f:
        template = engines["django"].from_string(f.read())

    with connection.cursor():
        rendered = template.render({
            "schema": sql.Identifier(schema).as_string(connection.connection),
            "owner": sql.Identifier(owner).as_string(connection.connection),
            "comment": sql.Literal(comment).as_string(connection.connection),
        })

    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(rendered)

    print(f'Schema "{schema}" created or updated successfully.')