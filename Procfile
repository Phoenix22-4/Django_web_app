release: python manage.py migrate && python manage.py createsuperuser --noinput
web: gunicorn AquaGuard.wsgi --bind 0.0.0.0:$PORT
worker: celery -A AquaGuard worker --loglevel=info