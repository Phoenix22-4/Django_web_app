# dashboard/middleware.py
import logging
from django.http import JsonResponse
from django.db import connection
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)

class DatabaseHealthCheckMiddleware:
    """
    Middleware to check database connectivity and handle connection issues gracefully.
    This prevents 500 errors when the database is sleeping or temporarily unavailable.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip health check for static files and admin
        if (request.path.startswith('/static/') or 
            request.path.startswith('/admin/') or
            request.path.startswith('/favicon.ico')):
            return self.get_response(request)
        
        try:
            # Test database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except Exception as e:
            logger.warning(f"Database connection issue: {e}")
            
            # Return a user-friendly error page instead of 500
            if request.path.startswith('/api/'):
                return JsonResponse({
                    'error': 'Database temporarily unavailable',
                    'message': 'Please try again in a few moments'
                }, status=503)
            else:
                # For regular pages, return a simple error page
                from django.http import HttpResponse
                return HttpResponse("""
                <html>
                <head><title>Service Temporarily Unavailable</title></head>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h1>🔄 Service Temporarily Unavailable</h1>
                    <p>The database is currently waking up. Please wait a moment and refresh the page.</p>
                    <p><a href="javascript:location.reload()">🔄 Refresh Page</a></p>
                    <p style="color: #666; font-size: 12px;">This usually takes 10-30 seconds</p>
                </body>
                </html>
                """, status=503)
        
        return self.get_response(request)
