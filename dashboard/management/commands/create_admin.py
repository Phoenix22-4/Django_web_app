import os
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates or updates an admin superuser from environment variables (ADMIN_USER, ADMIN_PASSWORD)'

    def handle(self, *args, **options):
        # Use your specific variable names
        username = os.environ.get('ADMIN_USER')
        password = os.environ.get('ADMIN_PASSWORD')
        
        # We also need an email, let's look for ADMIN_EMAIL
        # If it's not set, we'll create a default one.
        email = os.environ.get('ADMIN_EMAIL')
        if not email:
            if username:
                email = f"{username}@example.com" # Create a default email
                self.stdout.write(self.style.WARNING(f'ADMIN_EMAIL not set, defaulting to {email}'))
            else:
                email = "admin@example.com" # Fallback

        if not all([username, password]):
            raise CommandError('Missing one or both environment variables: ADMIN_USER, ADMIN_PASSWORD')

        try:
            # Check if user already exists
            user = User.objects.get(username=username)
            user.set_password(password)
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully updated password for admin user "{username}"'))
        
        except User.DoesNotExist:
            # Create a new user
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Successfully created new admin user "{username}"'))
