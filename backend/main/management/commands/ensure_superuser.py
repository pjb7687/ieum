import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates a default superuser if no superuser exists'

    def handle(self, *args, **options):
        # Check if any superuser exists
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.SUCCESS('Superuser already exists. Skipping creation.'))
            return

        # Get credentials from environment variables
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'changeme123')
        first_name = os.environ.get('DJANGO_SUPERUSER_FIRST_NAME', 'Admin')
        last_name = os.environ.get('DJANGO_SUPERUSER_LAST_NAME', 'User')
        institute = os.environ.get('DJANGO_SUPERUSER_INSTITUTE', 'System')

        # Use email as username
        username = email

        # Create the superuser
        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                institute=institute,
            )
            self.stdout.write(self.style.SUCCESS(
                f'Superuser "{username}" created successfully'
            ))
            self.stdout.write(self.style.WARNING(
                'Please change the default password immediately!'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Failed to create superuser: {str(e)}'
            ))
