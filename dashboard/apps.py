# dashboard/apps.py

from django.apps import AppConfig
import os

class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'

    def ready(self):
        if os.environ.get('RUN_MAIN', None) != 'true':
            return

        from .consumers import get_mqtt_client
        
        mqtt_client = get_mqtt_client()
        
        # This line is now temporarily disabled
        # mqtt_client.start()