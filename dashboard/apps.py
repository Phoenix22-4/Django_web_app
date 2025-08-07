# dashboard/apps.py
from django.apps import AppConfig
import os

class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'

    def ready(self):
        # This check prevents the code from running twice during development.
        if os.environ.get('RUN_MAIN', None) != 'true':
            return

        from .consumers import get_mqtt_client
        
        # Get the single instance of our client
        mqtt_client = get_mqtt_client()
        
        # Start the client and get the event object to wait on
        connection_event = mqtt_client.start()
        
        # This line will PAUSE the entire server startup until the connection is finished
        print("--> Waiting for MQTT connection to be established...")
        connection_successful = connection_event.wait(timeout=15)
        
        if connection_successful:
            print("--> MQTT connection confirmed. Proceeding with server startup.")
        else:
            print("!!! WARNING: Could not confirm MQTT connection after 15 seconds.")
            print("!!! The web server will start, but it may not receive data from devices.")