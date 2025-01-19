import os
from django.core.management.base import BaseCommand
from ...models import CustomUser
from dotenv import load_dotenv

load_dotenv()

class Command(BaseCommand):
    help = 'Create a superuser if it does not exist'

    def handle(self, *args, **kwargs):
        email_or_phone = os.getenv('SUPERUSER_ADMIN')
        password = os.getenv('SUPERUSER_PASSWORD')

        if not email_or_phone or not password:
            self.stdout.write(self.style.ERROR('SUPERUSER_EMAIL or SUPERUSER_PASSWORD is not set in the .env file'))
            return

        if not CustomUser.objects.filter(email_or_phone=email_or_phone).exists():
            CustomUser.objects.create_superuser(email_or_phone=email_or_phone, password=password)
            self.stdout.write(self.style.SUCCESS(f'Superuser created successfully with email: {email_or_phone}'))
        else:
            self.stdout.write(self.style.WARNING(f'Superuser with email {email_or_phone} already exists'))
