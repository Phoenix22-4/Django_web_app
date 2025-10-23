# dashboard/context_processors.py
"""
Context processors for AquaGuard Django application.
Provides global context variables for templates.
"""
from django.conf import settings
from django.urls import reverse
from django.utils import timezone


def canonical_url(request):
    """
    Context processor to provide canonical URL for SEO.
    Ensures canonical link tag is present in all templates.
    """
    return {
        'canonical_url': request.build_absolute_uri(),
        'current_year': timezone.now().year,
    }


def device_context(request):
    """
    Context processor to provide device-related context.
    """
    context = {}
    
    if request.user.is_authenticated:
        # Get user's primary device if available
        try:
            from .models import Device
            user_device = request.user.device_set.first()
            if user_device:
                context.update({
                    'user_device': user_device,
                    'has_pump': user_device.pump_present,
                    'device_tank_names': user_device.get_tank_names(),
                    'device_solenoid_names': user_device.get_solenoid_names(),
                })
        except Exception as e:
            print(f"Error getting device context: {e}")
    
    return context


def security_context(request):
    """
    Context processor to provide security-related context.
    """
    return {
        'is_secure': request.is_secure(),
        'debug_mode': settings.DEBUG,
        'admin_url': getattr(settings, 'ADMIN_URL', 'admin/'),
    }