# dashboard/apps.py
from django.apps import AppConfig
import os
import sys # <-- Add this import

class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'
    mqtt_client_started = False

    def ready(self):
        # --- THIS IS THE CRITICAL FIX ---
        # We only want to start the MQTT client for the main running server.
        # We must prevent it from starting during management commands like
        # 'migrate', 'shell', or 'createsuperuser'.
        is_management_command = any('manage.py' in arg for arg in sys.argv)

        if not is_management_command and not self.mqtt_client_started:
            from .consumers import get_mqtt_client
            
            print("--- Starting MQTT client from AppConfig ---")
            mqtt_client = get_mqtt_client()
            mqtt_client.start()
            
            self.mqtt_client_started = True