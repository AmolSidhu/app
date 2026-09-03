from django.core.management.base import BaseCommand
from functions.commands.all_commands import (confirm_admin, create_admin, create_schema,
                                             drive_health_check, run_migrations)

class Command(BaseCommand):
    def handle(self, *args, **options):
        
        primary_input = input("""Enter the command you would like to run, if you are unsure of the commands
                              \rEnter 'help' for a list of available commands: """).strip().lower()
        
        if primary_input == 'help':
            print("\nAvailable commands:")
            print("1. confirm_admin - Confirm an existing admin user")
            print("2. create_admin - Create a new admin user")
            print("3. create_schema - Create a new database schema")
            print("4. drive_health_check - Check the health of the drives")
            print("5. run_migrations - Run database migrations for all apps")
            
        elif primary_input == 'confirm_admin':
            confirm_admin()
        elif primary_input == 'create_admin':
            create_admin()
        elif primary_input == 'create_schema':
            create_schema()
        elif primary_input == 'drive_health_check':
            drive_health_check()
        elif primary_input == 'run_migrations':
            run_migrations()
        else:
            print("Invalid command. Please enter 'help' for a list of available commands.")