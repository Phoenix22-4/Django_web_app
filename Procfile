release: python manage.py makemigrations && python manage.py migrate && python create_admin_script.py
web: daphne -b 0.0.0.0 -p $PORT AquaGuard.asgi:application