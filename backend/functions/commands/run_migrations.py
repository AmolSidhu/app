from django.core import management
import json

def run_migrations():
    with open ('json/apps.json') as f:
        apps_data = json.load(f)
        
    apps = apps_data.get('apps', [])
    
    for app in apps:
        management.call_command('makemigrations', app)
        management.call_command('migrate', app)