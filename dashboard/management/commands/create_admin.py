#!/usr/bin/env python
import os
import sys
import django

print("=== ADMIN USER CREATION SCRIPT (Procfile Web) ===")
print("Starting admin user creation...")

try:
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AquaGuard.settings')
    django.setup()
    print("Django setup completed successfully")

    from django.contrib.auth import get_user_model
    User = get_user_model()
    print("User model imported successfully")

    # --- IMPORTANT: Hardcoded Credentials ---
    # This is generally NOT recommended for security.
    # Prefer environment variables if possible.
    username = 'Admin'
    password = 'Admin123!' # Your desired password
    email = 'admin@example.com' # Your desired email
    # ----------------------------------------

    print(f"Attempting to create/update admin user: {username}")
    print(f"Email: {email}")
    print(f"Password being set: {password}") # Explicitly print password

    # Using get_or_create to handle both creation and updates gracefully
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'email': email, 'is_staff': True, 'is_superuser': True}
    )

    # Always set/update the password, staff/superuser status, and email
    user.set_password(password)
    user.email = email
    user.is_staff = True
    user.is_superuser = True
    user.save()

    print("-" * 30) # Separator for clarity in logs
    if created:
        print(f'✅ SUCCESS: Created NEW admin user "{username}"')
    else:
        print(f'✅ SUCCESS: Updated EXISTING admin user "{username}"')

    # Confirm the details again, including the password
    print(f'   Username: {user.username}')
    print(f'   Password Set To: {password}') # Print password again
    print(f'   Email: {user.email}')
    print("-" * 30) # Separator

    print("=== ADMIN USER CREATION COMPLETED SUCCESSFULLY ===")
    # Allow the Procfile command to continue to Daphne
    sys.exit(0)


except Exception as e:
    print("-" * 30)
    print(f"❌ ERROR: Failed to create/update admin user: {str(e)}")
    print("-" * 30)
    print("=== ADMIN USER CREATION FAILED ===")
    # Stop the Procfile command from continuing to Daphne
    sys.exit(1)