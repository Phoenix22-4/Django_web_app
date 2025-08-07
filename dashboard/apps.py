# dashboard/apps.py (RUN MODE - FINAL VERSION)
from django.apps import AppConfig
import os

class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'
    mqtt_client_started = False

    def ready(self):
        # This code will now start the listener when you run the Daphne server.
        if not self.mqtt_client_started:
            from .consumers import get_mqtt_client
            
            print("--- Starting MQTT client from AppConfig ---")
            mqtt_client = get_mqtt_client()
            mqtt_client.start()
            
            self.mqtt_client_started = True