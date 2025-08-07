# dashboard/apps.py
from django.apps import AppConfig

class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'
    # We use a flag to make sure the startup code only runs once.
    mqtt_client_started = False

    def ready(self):
        # The 'ready' method is called by Django when the app is initialized.
        # This is the correct and safe place to start our background service.
        if not self.mqtt_client_started:
            from .consumers import get_mqtt_client
            
            print("--- Starting MQTT client from AppConfig ---")
            mqtt_client = get_mqtt_client()
            mqtt_client.start()
            
            # Set the flag to True so this code doesn't run again
            self.mqtt_client_started = True