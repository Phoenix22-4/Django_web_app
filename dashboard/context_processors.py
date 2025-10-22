# dashboard/context_processors.py
from django.conf import settings

def global_context(request):
    """Global context processor for templates"""
    return {
        'DEBUG': settings.DEBUG,
        'site_name': 'AquaGuard',
        'site_description': 'Smart Water Management System',
    }

def firebase_config(request):
    """Firebase configuration context processor"""
    return {
        'firebase_config': {
            'api_key': getattr(settings, 'FIREBASE_API_KEY', ''),
            'auth_domain': getattr(settings, 'FIREBASE_AUTH_DOMAIN', ''),
            'project_id': getattr(settings, 'FIREBASE_PROJECT_ID', ''),
            'storage_bucket': getattr(settings, 'FIREBASE_STORAGE_BUCKET', ''),
            'messaging_sender_id': getattr(settings, 'FIREBASE_MESSAGING_SENDER_ID', ''),
            'app_id': getattr(settings, 'FIREBASE_APP_ID', ''),
        }
    }
