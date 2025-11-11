# dashboard/enhanced_security.py
import logging
import time
import hashlib
import hmac
from django.http import HttpResponseForbidden, HttpResponse, JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.core.cache import cache
from django.utils.crypto import constant_time_compare
import json

logger = logging.getLogger(__name__)
CACHE_KEY_PREFIX = "rate_limit"

class EnhancedSecurityMiddleware(MiddlewareMixin):
    """
    Comprehensive security middleware implementing OWASP Top 10 mitigation.
    Uses Django cache for production-ready, scalable rate limiting.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)

    def process_request(self, request):
        client_ip = self.get_client_ip(request)
        current_time = time.time()

        if self._is_public_path(request.path):
            return None

        # General rate limiting (IP-based)
        if not self._check_general_rate_limit(client_ip, current_time):
            logger.warning(f"General rate limit exceeded for IP: {client_ip}")
            return HttpResponseForbidden("Rate limit exceeded. Please try again later.")

        # Login rate limiting (Username-based — 61-second window)
        if request.path == '/login/' and request.method == 'POST':
            username = request.POST.get('username')
            if username:
                if not self._monitor_login_attempts(username, current_time):
                    logger.warning(f"Login rate limit exceeded for username: {username} (IP: {client_ip})")
                    return JsonResponse({
                        "error": "Rate limit exceeded",
                        "message": f"Maximum {getattr(settings, 'RATE_LIMIT_LOGIN_ATTEMPTS', 5)} login attempts per {getattr(settings, 'RATE_LIMIT_LOGIN_WINDOW', 61)} seconds allowed for this username.",
                        "status": "rate_limited"
                    }, status=429)
            else:
                logger.warning(f"Login attempt missing username. IP: {client_ip}")

        return None

    def process_response(self, request, response):
        if self._is_public_path(request.path):
            response['X-Content-Type-Options'] = 'nosniff'
            return response

        # Security Headers
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://www.gstatic.com https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' wss: https:; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "object-src 'none'; "
            "media-src 'self'"
        )
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = (
            "geolocation=(), microphone=(), camera=(), "
            "payment=(), usb=(), magnetometer=(), gyroscope=(), "
            "accelerometer=(), ambient-light-sensor=(), "
            "autoplay=(), encrypted-media=(), fullscreen=(self)"
        )

        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'

        if 'Server' in response:
            del response['Server']
        return response

    def _is_public_path(self, path):
        public_paths = [
            '/', '/home/', '/about/', '/contact/',
            '/static/', '/media/', '/favicon.ico',
            '/sitemap.xml', '/robots.txt', '/sw.js',
            '/firebase-messaging-sw.js', '/manifest.json'
        ]
        return any(path.startswith(p) for p in public_paths)

    def _check_general_rate_limit(self, client_ip, current_time):
        max_requests = getattr(settings, 'RATE_LIMIT_REQUESTS_PER_MINUTE', 60)
        window_sec = 60
        window_start = int(current_time // window_sec)
        key = f"{CACHE_KEY_PREFIX}:general:{client_ip}:{window_start}"
        try:
            count = cache.get(key, 0)
            if count >= max_requests:
                return False
            cache.set(key, count + 1, timeout=window_sec)
            return True
        except Exception as e:
            logger.error(f"Cache error (general rate limit) for {client_ip}: {e}")
            return True  # Allow on cache failure

    def _monitor_login_attempts(self, username, current_time):
        max_attempts = getattr(settings, 'RATE_LIMIT_LOGIN_ATTEMPTS', 5)
        window_sec = getattr(settings, 'RATE_LIMIT_LOGIN_WINDOW', 61)
        window_start = int(current_time // window_sec)
        key = f"{CACHE_KEY_PREFIX}:login:{username}:{window_start}"
        try:
            count = cache.get(key, 0)
            if count >= max_attempts:
                logger.warning(f"Login limit active: {username} ({count} attempts in {window_sec}s)")
                return False
            new_count = count + 1
            cache.set(key, new_count, timeout=window_sec)
            if new_count >= max_attempts:
                logger.warning(f"Suspicious login activity: {username} ({new_count} attempts in {window_sec}s)")
            return True
        except Exception as e:
            logger.error(f"Cache error (login rate limit) for {username}: {e}")
            return True  # Allow on cache failure

    def get_client_ip(self, request):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        return xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR')

class SecurityAuditMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if self._is_public_path(request.path):
            return None
        client_ip = self.get_client_ip(request)
        
        if request.path == '/login/' and request.method == 'POST':
            username = request.POST.get('username', 'unknown')
            logger.info(f"Login attempt from IP {client_ip} for user: {username}")
        
        if request.path.startswith('/AquaSavvy-Control/') and request.user.is_authenticated:
            logger.info(f"Admin access from IP {client_ip} by user: {request.user.username}")
        
        if request.method in ['POST', 'PUT', 'DELETE'] and request.user.is_authenticated:
            logger.info(f"Sensitive operation {request.method} from IP {client_ip} by user: {request.user.username} on path: {request.path}")
        return None

    def _is_public_path(self, path):
        public_paths = [
            '/', '/home/', '/about/', '/contact/',
            '/static/', '/media/', '/favicon.ico',
            '/sitemap.xml', '/robots.txt', '/sw.js',
            '/firebase-messaging-sw.js', '/manifest.json'
        ]
        return any(path.startswith(p) for p in public_paths)

    def get_client_ip(self, request):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        return xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR')

class CSRFProtectionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if (self._is_public_path(request.path) or 
            request.method == 'GET' or 
            request.path.startswith('/api/iot_data/')):
            return None
        if request.path.startswith('/api/') and request.method == 'POST':
            if not request.META.get('HTTP_X_CSRFTOKEN'):
                logger.warning(f"Missing CSRF token from IP: {self.get_client_ip(request)}")
                return HttpResponseForbidden("CSRF token required")
        return None

    def _is_public_path(self, path):
        public_paths = [
            '/', '/home/', '/about/', '/contact/',
            '/static/', '/media/', '/favicon.ico',
            '/sitemap.xml', '/robots.txt', '/sw.js',
            '/firebase-messaging-sw.js', '/manifest.json'
        ]
        return any(path.startswith(p) for p in public_paths)

    def get_client_ip(self, request):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        return xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR')

# Utility functions (unchanged)
def generate_secure_token(data, secret_key=None):
    if secret_key is None:
        secret_key = settings.SECRET_KEY
    return hmac.new(secret_key.encode(), str(data).encode(), hashlib.sha256).hexdigest()

def verify_secure_token(token, data, secret_key=None):
    return constant_time_compare(token, generate_secure_token(data, secret_key))

def sanitize_filename(filename):
    import os, re
    filename = os.path.basename(filename)
    filename = re.sub(r'[^\w\-_.]', '', filename)
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255 - len(ext)] + ext
    return filename

def validate_device_id(device_id):
    import re
    return bool(re.match(r'^[a-zA-Z0-9_-]{3,50}$', device_id))

def log_security_event(event_type, details, request=None):
    log_data = {'event_type': event_type, 'details': details, 'timestamp': time.time()}
    if request:
        log_data.update({
            'ip_address': get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'path': request.path,
            'method': request.method,
        })
    logger.warning(f"Security Event: {json.dumps(log_data)}")

def get_client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    return xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR')