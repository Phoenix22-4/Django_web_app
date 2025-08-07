from django.apps import AppConfig
import os

class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'
    mqtt_client_started = False

    def ready(self):
        # This is the standard, correct way to start a background service.
        # It runs once when the main server process starts.
        if os.environ.get('RUN_MAIN', None) == 'true' and not self.mqtt_client_started:
            from .consumers import get_mqtt_client
            
            print("--- Starting MQTT client from AppConfig ---")
            mqtt_client = get_mqtt_client()
            mqtt_client.start()
            
            self.mqtt_client_started = True
