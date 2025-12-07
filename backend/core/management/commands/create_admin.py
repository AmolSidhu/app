from django.core.management.base import BaseCommand
from user.models import Credentials, AdminCredentials
from functions.generate_share_code import generate_share_code

class Command(BaseCommand):
    def handle(self, *args, **options):
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