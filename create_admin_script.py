#!/usr/bin/env python
import os
import sys
import django

print("=== ADMIN USER CREATION SCRIPT ===")
print("Starting admin user creation...")

try:
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AquaGuard.settings')
    django.setup()
    print("Django setup completed successfully")

    from django.contrib.auth import get_user_model
    User = get_user_model()
    print("User model imported successfully")

    # Create admin user
    username = 'Admin'
    password = 'Admin123!'
    email = 'admin@example.com'
    
    print(f"Creating admin user: {username}")
    print(f"Email: {email}")
    print(f"Password: {password}")

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
        print(f'✅ SUCCESS: Created new admin user "{username}"')
        print(f'   Username: {username}')
        print(f'   Password: {password}')
        print(f'   Email: {email}')
    else:
        print(f'✅ SUCCESS: Updated existing admin user "{username}"')
        print(f'   Username: {username}')
        print(f'   Password: {password}')
        print(f'   Email: {email}')

    print("=== ADMIN USER CREATION COMPLETED ===")

except Exception as e:
    print(f"❌ ERROR: Failed to create admin user: {str(e)}")
    sys.exit(1)
