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
        # Skip health check for static files, admin, and sitemap
        if (request.path.startswith('/static/') or 
            request.path.startswith('/admin/') or
            request.path.startswith('/favicon.ico') or
            request.path.startswith('/sitemap.xml') or
            request.path.startswith('/sw.js') or
            request.path.startswith('/firebase-messaging-sw.js')):
            return self.get_response(request)
        
        try:
            # Test database connection with timeout
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except Exception as e:
            logger.warning(f"Database connection issue: {e}")
            
            # Return a user-friendly error page instead of 500
            if request.path.startswith('/api/'):
                return JsonResponse({
                    'error': 'Database temporarily unavailable',
                    'message': 'Please try again in a few moments',
                    'status': 'database_waking_up'
                }, status=503)
            else:
                # For regular pages, return a beautiful error page
                from django.http import HttpResponse
                return HttpResponse("""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>AquaSavvy - Service Temporarily Unavailable</title>
                    <style>
                        body {
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            margin: 0;
                            padding: 0;
                            min-height: 100vh;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            color: white;
                        }
                        .container {
                            text-align: center;
                            background: rgba(255, 255, 255, 0.1);
                            padding: 40px;
                            border-radius: 20px;
                            backdrop-filter: blur(10px);
                            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
                            border: 1px solid rgba(255, 255, 255, 0.18);
                            max-width: 500px;
                            margin: 20px;
                        }
                        h1 { font-size: 2.5em; margin-bottom: 20px; }
                        p { font-size: 1.2em; margin-bottom: 30px; line-height: 1.6; }
                        .refresh-btn {
                            background: rgba(255, 255, 255, 0.2);
                            border: 2px solid rgba(255, 255, 255, 0.3);
                            color: white;
                            padding: 15px 30px;
                            border-radius: 50px;
                            text-decoration: none;
                            font-size: 1.1em;
                            transition: all 0.3s ease;
                            display: inline-block;
                        }
                        .refresh-btn:hover {
                            background: rgba(255, 255, 255, 0.3);
                            transform: translateY(-2px);
                        }
                        .status { 
                            color: #ffeb3b; 
                            font-size: 0.9em; 
                            margin-top: 20px;
                            opacity: 0.8;
                        }
                        .pulse {
                            animation: pulse 2s infinite;
                        }
                        @keyframes pulse {
                            0% { opacity: 1; }
                            50% { opacity: 0.5; }
                            100% { opacity: 1; }
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1 class="pulse">🔄 AquaSavvy</h1>
                        <h2>Service Temporarily Unavailable</h2>
                        <p>Our database is currently waking up from sleep mode. This is normal for cloud services and usually takes 10-30 seconds.</p>
                        <a href="javascript:location.reload()" class="refresh-btn">🔄 Refresh Page</a>
                        <p class="status">The page will automatically refresh when the service is ready</p>
                    </div>
                    <script>
                        // Auto-refresh every 5 seconds
                        setTimeout(() => {
                            location.reload();
                        }, 5000);
                    </script>
                </body>
                </html>
                """, status=503)
        
        return self.get_response(request)
