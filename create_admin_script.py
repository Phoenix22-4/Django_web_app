#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AquaGuard.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Create admin user
username = 'Admin'
password = 'Admin123!'
email = 'admin@example.com'

user, created = User.objects.get_or_create(
    username=username, 
    defaults={'email': email, 'is_staff': True, 'is_superuser': True}
)

user.set_password(password)
user.email = email
user.is_staff = True
user.is_superuser = True
user.save()

if created:
    print(f'Successfully created new admin user "{username}"')
else:
    print(f'Successfully updated admin user "{username}"')
