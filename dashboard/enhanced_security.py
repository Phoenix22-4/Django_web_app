"""
Enhanced security middleware and utilities for AquaGuard Django application.
Implements comprehensive OWASP Top 10 mitigation strategies.
"""
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
from collections import defaultdict
import json

logger = logging.getLogger(__name__)

class EnhancedSecurityMiddleware(MiddlewareMixin):
    """
    Comprehensive security middleware implementing OWASP Top 10 mitigation.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.request_counts = defaultdict(list)
        self.login_attempts = defaultdict(list)
        super().__init__(get_response)
    
    def process_request(self, request):
        """Process incoming requests with security checks."""
        client_ip = self.get_client_ip(request)
        current_time = time.time()
        
        # Skip security checks for static files and public pages
        if self._is_public_path(request.path):
            return None
        
        # Rate limiting
        if not self._check_rate_limit(client_ip, current_time):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return HttpResponseForbidden("Rate limit exceeded. Please try again later.")
        
        # Login attempt monitoring
        if request.path == '/login/' and request.method == 'POST':
            self._monitor_login_attempts(client_ip, current_time)
        
        # Security headers will be added in process_response
        return None
    
    def process_response(self, request, response):
        """Add security headers and process response."""
        # Skip security headers for static files and public pages
        if self._is_public_path(request.path):
            # Only add minimal headers for public pages
            response['X-Content-Type-Options'] = 'nosniff'
            return response
        
        # Enhanced Content Security Policy
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
        
        # Security headers
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
        
        # HSTS for HTTPS
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        # Remove server information
        if 'Server' in response:
            del response['Server']
        
        return response
    
    def _is_public_path(self, path):
        """Check if path is public and should skip security checks."""
        public_paths = [
            '/', '/home/', '/about/', '/contact/',
            '/static/', '/media/', '/favicon.ico',
            '/sitemap.xml', '/robots.txt', '/sw.js',
            '/firebase-messaging-sw.js',
            '/manifest.json'  # <-- ✅ THIS IS THE FIX
        ]
        return any(path.startswith(public_path) for public_path in public_paths)
    
    def _check_rate_limit(self, client_ip, current_time):
        """Check if client has exceeded rate limit."""
        # Clean old entries (older than 1 minute)
        self.request_counts[client_ip] = [
            req_time for req_time in self.request_counts[client_ip]
            if current_time - req_time < 60
        ]
        
        # Check rate limit (60 requests per minute)
        max_requests = getattr(settings, 'RATE_LIMIT_REQUESTS_PER_MINUTE', 60)
        if len(self.request_counts[client_ip]) >= max_requests:
            return False
        
        # Add current request
        self.request_counts[client_ip].append(current_time)
        return True
    
    def _monitor_login_attempts(self, client_ip, current_time):
        """Monitor and log login attempts."""
        # Clean old entries (older than 5 minutes)
        self.login_attempts[client_ip] = [
            attempt_time for attempt_time in self.login_attempts[client_ip]
            if current_time - attempt_time < 300
        ]
        
        # Add current attempt
        self.login_attempts[client_ip].append(current_time)
        
        # Log suspicious activity
        max_attempts = getattr(settings, 'RATE_LIMIT_LOGIN_ATTEMPTS', 5)
        if len(self.login_attempts[client_ip]) >= max_attempts:
            logger.warning(f"Suspicious login activity from IP: {client_ip} - {len(self.login_attempts[client_ip])} attempts in 5 minutes")
    
    def get_client_ip(self, request):
        """Get client IP address from request headers."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class SecurityAuditMiddleware(MiddlewareMixin):
    """
    Security audit logging middleware.
    """
    
    def process_request(self, request):
        """Log security-relevant events."""
        # Skip logging for public pages
        if self._is_public_path(request.path):
            return None
        
        client_ip = self.get_client_ip(request)
        
        # Log authentication attempts
        if request.path == '/login/' and request.method == 'POST':
            username = request.POST.get('username', 'unknown')
            logger.info(f"Login attempt from IP {client_ip} for user: {username}")
        
        # Log admin access
        if request.path.startswith('/AquaSavvy-Control/') and request.user.is_authenticated:
            logger.info(f"Admin access from IP {client_ip} by user: {request.user.username}")
        
        # Log sensitive operations
        if request.method in ['POST', 'PUT', 'DELETE'] and request.user.is_authenticated:
            logger.info(f"Sensitive operation {request.method} from IP {client_ip} by user: {request.user.username} on path: {request.path}")
        
        return None
    
    def _is_public_path(self, path):
        """Check if path is public."""
        public_paths = [
            '/', '/home/', '/about/', '/contact/',
            '/static/', '/media/', '/favicon.ico',
            '/sitemap.xml', '/robots.txt', '/sw.js',
            '/firebase-messaging-sw.js',
            '/manifest.json'  # <-- ✅ THIS IS THE FIX
        ]
        return any(path.startswith(public_path) for public_path in public_paths)
    
    def get_client_ip(self, request):
        """Get client IP address from request headers."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class CSRFProtectionMiddleware(MiddlewareMixin):
    """
    Enhanced CSRF protection middleware.
    """
    
    def process_request(self, request):
        """Enhanced CSRF protection for sensitive endpoints."""
        # Skip CSRF checks for public pages and GET requests
        if (self._is_public_path(request.path) or 
            request.method == 'GET' or 
            request.path.startswith('/api/iot_data/')):  # IoT data endpoint needs special handling
            return None
        
        # For API endpoints, ensure CSRF token is present
        if request.path.startswith('/api/') and request.method == 'POST':
            csrf_token = request.META.get('HTTP_X_CSRFTOKEN')
            if not csrf_token:
                logger.warning(f"Missing CSRF token for API request from IP: {self.get_client_ip(request)}")
                return HttpResponseForbidden("CSRF token required")
        
        return None
    
    def _is_public_path(self, path):
        """Check if path is public."""
        public_paths = [
            '/', '/home/', '/about/', '/contact/',
            '/static/', '/media/', '/favicon.ico',
            '/sitemap.xml', '/robots.txt', '/sw.js',
            '/firebase-messaging-sw.js',
            '/manifest.json'  # <-- ✅ THIS IS THE FIX
        ]
        return any(path.startswith(public_path) for public_path in public_paths)
    
    def get_client_ip(self, request):
        """Get client IP address from request headers."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

# ... (rest of the file from generate_secure_token downwards is unchanged) ...

def generate_secure_token(data, secret_key=None):
    """
    Generate a secure token using HMAC.
    
    Args:
        data: Data to sign
        secret_key: Secret key (defaults to Django SECRET_KEY)
    
    Returns:
        Secure token string
    """
    if secret_key is None:
        secret_key = settings.SECRET_KEY
    
    return hmac.new(
        secret_key.encode('utf-8'),
        str(data).encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

def verify_secure_token(token, data, secret_key=None):
    """
    Verify a secure token.
    
    Args:
        token: Token to verify
        data: Original data
        secret_key: Secret key (defaults to Django SECRET_KEY)
    
    Returns:
        True if token is valid, False otherwise
    """
    expected_token = generate_secure_token(data, secret_key)
    return constant_time_compare(token, expected_token)

def sanitize_filename(filename):
    """
    Sanitize filename to prevent directory traversal attacks.
    
    Args:
        filename: Original filename
    
    Returns:
        Sanitized filename
    """
    import os
    import re
    
    # Remove directory traversal attempts
    filename = os.path.basename(filename)
    
    # Remove dangerous characters
    filename = re.sub(r'[^\w\-_\.]', '', filename)
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename

def validate_device_id(device_id):
    """
    Validate device ID format for security.
    
    Args:
        device_id: Device ID to validate
    
    Returns:
        True if valid, False otherwise
    """
    import re
    
    # Device ID should be alphanumeric with hyphens and underscores
    # Length between 3 and 50 characters
    pattern = r'^[a-zA-Z0-9_-]{3,50}$'
    return bool(re.match(pattern, device_id))

def log_security_event(event_type, details, request=None):
    """
    Log security events for monitoring.
    
    Args:
        event_type: Type of security event
        details: Event details
        request: Django request object (optional)
    """
    log_data = {
        'event_type': event_type,
        'details': details,
        'timestamp': time.time(),
    }
    
    if request:
        log_data.update({
            'ip_address': get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'path': request.path,
            'method': request.method,
        })
    
    logger.warning(f"Security Event: {json.dumps(log_data)}")

def get_client_ip(request):
    """Get client IP address from request headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip