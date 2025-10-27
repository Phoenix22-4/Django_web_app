# AquaGuard/settings.py
from pathlib import Path
import os
import dj_database_url
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

# --- CORE Django Configuration (Security: ENV variables only) ---
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-fallback-for-local-dev')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# ✅ FIX: Correctly configure ALLOWED_HOSTS for Railway and local development
RAILWAY_HOST = os.environ.get('RAILWAY_STATIC_URL')
ALLOWED_HOSTS = ['localhost', '127.0.0.1'] # Always allow local
if RAILWAY_HOST:
    ALLOWED_HOSTS.append(RAILWAY_HOST)
# Add any custom domain you might have here from environment variables if needed
# CUSTOM_DOMAIN = os.environ.get('CUSTOM_DOMAIN')
# if CUSTOM_DOMAIN:
#     ALLOWED_HOSTS.append(CUSTOM_DOMAIN)

# ✅ FIX: Correctly configure CSRF_TRUSTED_ORIGINS for Railway and potentially local HTTPS
CSRF_TRUSTED_ORIGINS = []
if RAILWAY_HOST:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RAILWAY_HOST}")
# if CUSTOM_DOMAIN:
#     CSRF_TRUSTED_ORIGINS.append(f"https://{CUSTOM_DOMAIN}")
if DEBUG:
    # Allow local origins only if DEBUG is True
    CSRF_TRUSTED_ORIGINS.extend(['http://localhost:8000', 'http://127.0.0.1:8000'])

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'channels',
    'dashboard.apps.DashboardConfig',
]

# --- CORRECTED MIDDLEWARE ORDER (Crucial for security and function) ---
MIDDLEWARE = [
    # 1. SECURITY & HOSTING (Must be first)
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

    # 2. CORE SESSION MANAGEMENT (Must run before anything uses 'request.session')
    'django.contrib.sessions.middleware.SessionMiddleware',

    # 3. CUSTOM PRE-AUTH CHECKS (Run checks before authentication)
    'dashboard.middleware.DatabaseHealthCheckMiddleware',

    # 4. CORE AUTHENTICATION AND CSRF (Must run after SessionMiddleware)
    'django.middleware.common.CommonMiddleware', # CommonMiddleware needed for locale, etc., before auth
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    # 5. CUSTOM ENHANCED SECURITY (Run after authentication is complete)
    'dashboard.enhanced_security.EnhancedSecurityMiddleware',
    'dashboard.enhanced_security.SecurityAuditMiddleware',
    # 'dashboard.enhanced_security.CSRFProtectionMiddleware', # Django's CsrfViewMiddleware usually sufficient

    # 6. CORE CONTENT/MESSAGING (Must run near the end)
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'AquaGuard.urls' # Ensure this matches your project folder name
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'dashboard' / 'templates'], # Correct path using pathlib
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug', # Often useful
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'dashboard.context_processors.canonical_url',
                'dashboard.context_processors.device_context',
                'dashboard.context_processors.security_context',
                'dashboard.context_processors.firebase_context',
            ],
        },
    },
]
WSGI_APPLICATION = 'AquaGuard.wsgi.application' # Ensure this matches your project folder name

# --- DATABASE CONFIGURATION ---
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    print("Found DATABASE_URL environment variable. Using PostgreSQL.")
    try:
        DATABASES = {
            # Ensure SSL is required for Railway Postgres
            'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=True)
        }
        print("✅ Database configuration loaded successfully")
    except Exception as e:
        print(f"❌ Error parsing DATABASE_URL: {e}")
        print("Falling back to SQLite database.")
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
else:
    print("No DATABASE_URL found. Using local SQLite database.")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC' # Or your specific timezone like 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

# Static files (WhiteNoise configuration is correct)
STATIC_URL = '/static/'
# Correct STATICFILES_DIRS using pathlib
STATICFILES_DIRS = [BASE_DIR / 'dashboard' / 'static']
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Channels Configuration ---
ASGI_APPLICATION = 'AquaGuard.asgi.application' # Ensure this matches your project folder name
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [REDIS_URL],
        },
    },
}

# Session settings (Ensure these match your security requirements)
SESSION_ENGINE = 'django.contrib.sessions.backends.db' # Or cache-based for performance
SESSION_COOKIE_AGE = 1800 # 30 minutes idle timeout
SESSION_EXPIRE_AT_BROWSER_CLOSE = True # Log out when browser closes

# Authentication URLs
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'device_list' # Where to go after successful login
LOGOUT_REDIRECT_URL = 'public_home' # Where to go after logout

# Firebase Admin SDK Configuration - Environment Variables Only
FIREBASE_CREDENTIALS = os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON', '')
if not FIREBASE_CREDENTIALS and not DEBUG: # Only warn in production
    print("WARNING: 'FIREBASE_SERVICE_ACCOUNT_JSON' environment variable not found. Firebase Admin SDK will not be initialized.")

# Firebase Configuration (For Frontend/Templates) - Use environment variables
FIREBASE_API_KEY = os.environ.get('FIREBASE_WEB_API_KEY', '')
FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID', '')
FIREBASE_MESSAGING_SENDER_ID = os.environ.get('FIREBASE_MESSAGING_SENDER_ID', '')
FIREBASE_APP_ID = os.environ.get('FIREBASE_WEB_APP_ID', '')
FIREBASE_MEASUREMENT_ID = os.environ.get('FIREBASE_MEASUREMENT_ID', '') # Optional
VAPID_PUBLIC_KEY = os.environ.get('VAPID_PUBLIC_KEY', '') # For web push

# Site ID for sitemaps
SITE_ID = 1

# --- ENHANCED SECURITY SETTINGS ---
ADMIN_URL = os.environ.get('ADMIN_URL', 'admin/') # Default back to 'admin/' if not set

# Enhanced password validation (Good settings)
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Enhanced session security (Good settings)
SESSION_COOKIE_HTTPONLY = True # Prevents client-side script access
SESSION_COOKIE_SECURE = not DEBUG # Send only over HTTPS in production
SESSION_COOKIE_SAMESITE = 'Lax' # Default protection against CSRF, 'Strict' can break some flows

# Enhanced CSRF security (Good settings)
CSRF_COOKIE_HTTPONLY = False # Must be False for JavaScript access (e.g., AJAX)
CSRF_COOKIE_SECURE = not DEBUG # Send only over HTTPS in production
CSRF_COOKIE_SAMESITE = 'Lax' # Default protection, 'Strict' is more secure but can be restrictive
CSRF_FAILURE_VIEW = 'dashboard.views.csrf_failure_view' # Custom view for CSRF errors

# Production security settings (Applied when DEBUG=False)
if not DEBUG:
    SECURE_SSL_REDIRECT = True # Redirect HTTP to HTTPS
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https') # Trust proxy headers
    SECURE_HSTS_SECONDS = 31536000 # 1 year HSTS
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True # Submit to browser preload lists (requires commitment)

# Rate limiting settings (Used by your custom middleware/decorators)
RATE_LIMIT_ENABLED = True
RATE_LIMIT_REQUESTS_PER_MINUTE = int(os.environ.get('RATE_LIMIT_REQUESTS_PER_MINUTE', 60))
RATE_LIMIT_LOGIN_ATTEMPTS = int(os.environ.get('RATE_LIMIT_LOGIN_ATTEMPTS', 5))
RATE_LIMIT_LOGIN_WINDOW = int(os.environ.get('RATE_LIMIT_LOGIN_WINDOW', 300)) # 5 minutes

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO', # Set to 'DEBUG' for more verbose logs during development
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'dashboard': { # Your app's logger
             'handlers': ['console'],
             'level': 'INFO', # Or 'DEBUG'
             'propagate': False,
        }
    },
}