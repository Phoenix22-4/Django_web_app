release: python manage.py migrate && python manage.py create_admin
web: daphne -b 0.0.0.0 -p $PORT AquaGuard.asgi:application