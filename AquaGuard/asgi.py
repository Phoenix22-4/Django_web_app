# AquaGuard/asgi.py
import os
from django.core.asgi import get_asgi_application

# This line MUST be at the top. It initializes Django's settings.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AquaGuard.settings')

# --- NEW: START THE MQTT CLIENT FIRST ---
# We import the client from the consumers file
from dashboard.consumers import mqtt_listener_client

print("--- Starting MQTT client from asgi.py ---")
# This command starts the background listener thread.
mqtt_listener_client.start()
# --- END NEW SECTION ---

# Now that the listener is running, we can set up the web application.
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import AquaGuard.routing

application = ProtocolType_Router({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            AquaGuard.routing.websocket_urlpatterns
        )
    ),
})