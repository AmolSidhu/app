from user.models import Credentials, AdminCredentials
from functions.check_functions.generate_share_code import generate_share_code
from django.db import connection, transaction
from django.template import engines
from django.core import management
from psycopg import sql

import json
import shutil

def confirm_admin():
    username = input("Enter username: ")
    email = input("Enter email: ")
    
    check_user = Credentials.objects.filter(
        username=username, email=email).first()

    if check_user is None:
        print("User does not exists.")
        return
    
    check_existing_admin = AdminCredentials.objects.filter(
        admin_username=check_user).first()
    if check_existing_admin is None:
        print("Admin user does not exists.")
        return
    
    if check_existing_admin.active_admin:
        print("User is already an admin.")
        return
    
    check_existing_admin.active_admin = True
    check_existing_admin.save()
    
    print(f"Admin user {username} confirmed successfully.")
    
def create_admin():
    username = input("Enter username: ")
    email = input("Enter email: ")

    check_user = Credentials.objects.filter(
        username=username, email=email).first()

    if check_user is None:
        print("User does not exists.")
        return
    
    check_existing_admin = AdminCredentials.objects.filter(
        admin_username=check_user).first()
    if check_existing_admin is not None:
        print("Admin user already exists.")
        return
    
    create_admin = AdminCredentials(
        admin_username=check_user,
        admin_email=email,
        admin_code=generate_share_code(),
    )
    create_admin.save()
    print(f"Admin user {username} created successfully.")
    
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
    
def drive_health_check():
    username = input("Enter username:")
    email = input("Enter email: ")
    
    check_user = Credentials.objects.filter(
        username=username, email=email).first()
    if check_user is None:
        print("User does not exist")
        return
    
    print(f"Checking drive health for user: {username}")
    print(f"check_user: {check_user}")
    
    check_existing_admin = AdminCredentials.objects.filter(
        admin_username=check_user).first()
    if check_existing_admin is None:
        print("Admin user does not exist")
        return
    
    with open('json/directory.json') as f:
        directory_data = json.load(f)
    if not directory_data:
        print("Directory data is empty")
        return

    drives = []

    for key, path in directory_data.items():
        split_entry = path.split('/')
        drive_name = split_entry[0]
        if drive_name not in drives:
            drives.append(drive_name)

    for drive in drives:
        try:
            usage = shutil.disk_usage(drive)

            total_gb = (usage.total / (1024**3)).__round__(2)
            used_gb = (usage.used / (1024**3)).__round__(2)
            free_gb = (usage.free / (1024**3)).__round__(2)
            percent_full = (used_gb / total_gb * 100).__round__(2)

            print(f"\nDrive: {drive}")
            print(f"Total: {total_gb} GB")
            print(f"Used: {used_gb} GB")
            print(f"Free: {free_gb} GB")
            print(f"Percent full: {percent_full} %")

            if percent_full >= 95:
                print("Drive is 95% full")
            elif percent_full >= 85:
                print("Drive is 85% full")
            elif percent_full >= 70:
                print("Drive is 70% full")
            else:
                print("Drive is healthy ")

        except Exception as e:
            print(f"Error checking drive {drive}: {e}")
            
def run_migrations():
    with open ('json/apps.json') as f:
        apps_data = json.load(f)
        
    apps = apps_data.get('apps', [])
    
    for app in apps:
        management.call_command('makemigrations', app)
        management.call_command('migrate', app)