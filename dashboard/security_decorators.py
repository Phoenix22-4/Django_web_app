# dashboard/security_decorators.py
"""
Security-first decorators for AquaGuard Django application.
Implements OWASP Top 10 mitigation strategies.
"""
import json
import logging
from functools import wraps
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.core.validators import validate_email
import re
import time
from collections import defaultdict

logger = logging.getLogger(__name__)

# Rate limiting storage (in production, use Redis)
_rate_limit_storage = defaultdict(list)

def rate_limit(max_requests=60, window_seconds=60, key_func=None):
    """
    Rate limiting decorator with configurable limits.
    
    Args:
        max_requests: Maximum requests allowed in window
        window_seconds: Time window in seconds
        key_func: Function to generate rate limit key (defaults to IP)
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Generate rate limit key
            if key_func:
                key = key_func(request)
            else:
                key = get_client_ip(request)
            
            current_time = time.time()
            
            # Clean old entries
            _rate_limit_storage[key] = [
                req_time for req_time in _rate_limit_storage[key]
                if current_time - req_time < window_seconds
            ]
            
            # Check rate limit
            if len(_rate_limit_storage[key]) >= max_requests:
                logger.warning(f"Rate limit exceeded for key: {key}")
                return JsonResponse({
                    'error': 'Rate limit exceeded',
                    'message': f'Maximum {max_requests} requests per {window_seconds} seconds allowed',
                    'status': 'rate_limited'
                }, status=429)
            
            # Add current request
            _rate_limit_storage[key].append(current_time)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def secure_api_view(require_auth=True, allowed_methods=['POST'], rate_limit_requests=30):
    """
    Comprehensive security decorator for API views.
    
    Args:
        require_auth: Whether authentication is required
        allowed_methods: List of allowed HTTP methods
        rate_limit_requests: Rate limit per minute
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Method validation
            if request.method not in allowed_methods:
                return JsonResponse({
                    'error': 'Method not allowed',
                    'status': 'error'
                }, status=405)
            
            # Authentication check
            if require_auth and not request.user.is_authenticated:
                return JsonResponse({
                    'error': 'Authentication required',
                    'status': 'error'
                }, status=401)
            
            # Rate limiting
            if rate_limit_requests > 0:
                current_time = time.time()
                client_ip = get_client_ip(request)
                
                # Clean old entries
                _rate_limit_storage[client_ip] = [
                    req_time for req_time in _rate_limit_storage[client_ip]
                    if current_time - req_time < 60
                ]
                
                # Check rate limit
                if len(_rate_limit_storage[client_ip]) >= rate_limit_requests:
                    logger.warning(f"API rate limit exceeded for IP: {client_ip}")
                    return JsonResponse({
                        'error': 'Rate limit exceeded',
                        'status': 'error'
                    }, status=429)
                
                # Add current request
                _rate_limit_storage[client_ip].append(current_time)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def validate_json_input(required_fields=None, optional_fields=None, max_length=10000):
    """
    Validate JSON input with comprehensive security checks.
    
    Args:
        required_fields: List of required field names
        optional_fields: List of optional field names with types
        max_length: Maximum request body length
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Check content length
            if len(request.body) > max_length:
                return JsonResponse({
                    'error': 'Request too large',
                    'status': 'error'
                }, status=413)
            
            # Parse JSON
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({
                    'error': 'Invalid JSON format',
                    'status': 'error'
                }, status=400)
            
            # Validate required fields
            if required_fields:
                for field in required_fields:
                    if field not in data:
                        return JsonResponse({
                            'error': f'Missing required field: {field}',
                            'status': 'error'
                        }, status=400)
            
            # Validate field types and content
            if optional_fields:
                for field, field_type in optional_fields.items():
                    if field in data:
                        value = data[field]
                        
                        # Type validation
                        if field_type == 'string' and not isinstance(value, str):
                            return JsonResponse({
                                'error': f'Field {field} must be a string',
                                'status': 'error'
                            }, status=400)
                        elif field_type == 'integer' and not isinstance(value, int):
                            return JsonResponse({
                                'error': f'Field {field} must be an integer',
                                'status': 'error'
                            }, status=400)
                        elif field_type == 'boolean' and not isinstance(value, bool):
                            return JsonResponse({
                                'error': f'Field {field} must be a boolean',
                                'status': 'error'
                            }, status=400)
                        
                        # Content validation for strings
                        if isinstance(value, str):
                            # Length validation
                            if len(value) > 1000:  # Reasonable limit
                                return JsonResponse({
                                    'error': f'Field {field} too long',
                                    'status': 'error'
                                }, status=400)
                            
                            # XSS prevention - basic check
                            if any(tag in value.lower() for tag in ['<script', '<iframe', '<object', '<embed']):
                                return JsonResponse({
                                    'error': f'Field {field} contains invalid content',
                                    'status': 'error'
                                }, status=400)
            
            # Add validated data to request
            request.validated_data = data
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def device_ownership_required(view_func):
    """
    Ensure user owns the device they're trying to access.
    Expects device_id in kwargs or request.validated_data.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        device_id = kwargs.get('device_id') or request.validated_data.get('device_id')
        
        if not device_id:
            return JsonResponse({
                'error': 'Device ID required',
                'status': 'error'
            }, status=400)
        
        # Validate device_id format (basic security check)
        if not re.match(r'^[a-zA-Z0-9_-]{3,50}$', device_id):
            return JsonResponse({
                'error': 'Invalid device ID format',
                'status': 'error'
            }, status=400)
        
        try:
            from .models import Device
            device = get_object_or_404(Device, device_id=device_id)
            
            # Check ownership
            if device.owner != request.user and not request.user.is_superuser:
                logger.warning(f"Unauthorized device access attempt by user {request.user.username} for device {device_id}")
                return JsonResponse({
                    'error': 'Access denied',
                    'status': 'error'
                }, status=403)
            
            # Add device to request for use in view
            request.device = device
            return view_func(request, *args, **kwargs)
            
        except Exception as e:
            logger.error(f"Error in device ownership check: {e}")
            return JsonResponse({
                'error': 'Device access error',
                'status': 'error'
            }, status=500)
    
    return wrapper

def get_client_ip(request):
    """Get client IP address from request headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def sanitize_input(value, max_length=1000):
    """
    Sanitize user input to prevent XSS and other attacks.
    
    Args:
        value: Input value to sanitize
        max_length: Maximum allowed length
    
    Returns:
        Sanitized value
    """
    if not isinstance(value, str):
        return value
    
    # Length check
    if len(value) > max_length:
        value = value[:max_length]
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', '\x00', '\r', '\n']
    for char in dangerous_chars:
        value = value.replace(char, '')
    
    return value.strip()

class SecureAPIView(View):
    """
    Base class for secure API views with built-in security features.
    """
    require_auth = True
    allowed_methods = ['POST']
    rate_limit_requests = 30
    required_fields = []
    optional_fields = {}
    
    def dispatch(self, request, *args, **kwargs):
        # Apply security decorators
        view_func = super().dispatch
        view_func = secure_api_view(
            require_auth=self.require_auth,
            allowed_methods=self.allowed_methods,
            rate_limit_requests=self.rate_limit_requests
        )(view_func)
        
        if self.required_fields or self.optional_fields:
            view_func = validate_json_input(
                required_fields=self.required_fields,
                optional_fields=self.optional_fields
            )(view_func)
        
        return view_func(request, *args, **kwargs)
