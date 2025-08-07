# AquaGuard/asgi.py
import os
from django.core.asgi import get_asgi_application

# This line MUST be at the top. It initializes Django's settings and apps.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AquaGuard.settings')
django_asgi_app = get_asgi_application()

# Now that Django is fully initialized, we can safely import the rest.
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import AquaGuard.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            AquaGuard.routing.websocket_urlpatterns
        )
    ),
})