#AquaGuard/routing.py
from django.urls import path
from dashboard.consumers import DashboardConsumer

websocket_urlpatterns = [
    path('ws/dashboard/<str:device_id>/', DashboardConsumer.as_asgi()),
]
