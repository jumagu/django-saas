from django.core.management import BaseCommand

class Command(BaseCommand):
    def handle(self, *args: any, **options: any):
        print("Hello World")