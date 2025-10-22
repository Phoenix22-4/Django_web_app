# dashboard/security.py
from django.http import HttpResponseForbidden, HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect
import logging
import time

logger = logging.getLogger(__name__)

class ForceLogoutMiddleware(MiddlewareMixin):
    """Enhanced security middleware - log security events"""
    
    def process_request(self, request):
        # Only apply security to login and beyond, not to public home
        if (request.user.is_authenticated and 
            not request.path.startswith('/static/') and 
            not request.path in ['/', '/home/', '/about/', '/contact/'] and
            not request.path.startswith('/sitemap') and
            not request.path.startswith('/robots.txt')):
            
            # Log security events but don't force logout
            if not request.session.get('_auth_user_id'):
                logger.warning(f"Security: Invalid session detected for user {request.user.username}")
        
        return None

class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add security headers to all responses"""
    
    def process_response(self, request, response):
        # Skip security headers for static files and public pages to avoid blocking functionality
        if (request.path.startswith('/static/') or 
            request.path.startswith('/media/') or
            request.path in ['/', '/home/', '/about/', '/contact/'] or
            request.path.startswith('/sitemap') or
            request.path.startswith('/robots.txt')):
            # Only add minimal headers for public pages to ensure Google can access
            response['X-Content-Type-Options'] = 'nosniff'
            return response
        
        # Content Security Policy - more permissive for functionality
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://www.gstatic.com https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' wss: https:; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        
        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = (
            "geolocation=(), microphone=(), camera=(), "
            "payment=(), usb=(), magnetometer=(), gyroscope=(), "
            "accelerometer=(), ambient-light-sensor=(), "
            "autoplay=(), encrypted-media=()"
        )
        
        # HSTS for HTTPS
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        return response

class RateLimitMiddleware(MiddlewareMixin):
    """Simple rate limiting middleware"""
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.request_counts = {}
    
    def process_request(self, request):
        # Skip rate limiting for public pages
        if (request.path in ['/', '/home/', '/about/', '/contact/'] or
            request.path.startswith('/static/') or
            request.path.startswith('/sitemap') or
            request.path.startswith('/robots.txt')):
            return None
            
        # Simple rate limiting based on IP for protected pages
        client_ip = self.get_client_ip(request)
        current_time = int(time.time())
        
        # Clean old entries (older than 1 minute)
        if client_ip in self.request_counts:
            self.request_counts[client_ip] = [
                req_time for req_time in self.request_counts[client_ip]
                if current_time - req_time < 60
            ]
        else:
            self.request_counts[client_ip] = []
        
        # Check rate limit (100 requests per minute)
        if len(self.request_counts[client_ip]) >= 100:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return HttpResponseForbidden("Rate limit exceeded. Please try again later.")
        
        # Add current request
        self.request_counts[client_ip].append(current_time)
        
        return None
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class AuditLogMiddleware(MiddlewareMixin):
    """Security audit logging middleware"""
    
    def process_request(self, request):
        # Skip logging for public pages
        if (request.path in ['/', '/home/', '/about/', '/contact/'] or
            request.path.startswith('/static/') or
            request.path.startswith('/sitemap') or
            request.path.startswith('/robots.txt')):
            return None
            
        # Log authentication attempts
        if request.path == '/login/' and request.method == 'POST':
            username = request.POST.get('username', 'unknown')
            logger.info(f"Login attempt from IP {self.get_client_ip(request)} for user: {username}")
        
        # Log admin access
        if request.path.startswith('/admin/') and request.user.is_authenticated:
            logger.info(f"Admin access from IP {self.get_client_ip(request)} by user: {request.user.username}")
        
        # Log sensitive operations
        if request.method in ['POST', 'PUT', 'DELETE'] and request.user.is_authenticated:
            logger.info(f"Sensitive operation {request.method} from IP {self.get_client_ip(request)} by user: {request.user.username} on path: {request.path}")
        
        return None
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
