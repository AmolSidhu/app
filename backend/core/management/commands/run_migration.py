from django.core.management.base import BaseCommand
from django.core import management

class Command(BaseCommand):
    def handle(self, *args, **options):
        apps = [
            'user',
            'auth',
            'contenttypes',
            'sessions',
            'admin',
            'pictures',
            'videos',
            'streams',
            'management',
            'analytics',
            'youtube',
            'music',
            'articles',
            'files',
            'mtg',
            ]

        for app in apps:
            management.call_command('makemigrations', app)
            management.call_command('migrate', app)