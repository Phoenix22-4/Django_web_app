# AquaGuard/settings.py
from pathlib import Path
import os
import dj_database_url
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

# ... (Keep SECRET_KEY, DEBUG, ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS as they were) ...
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-fallback-for-local-dev')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = [os.environ.get('RAILWAY_STATIC_URL', '.railway.app')]
CSRF_TRUSTED_ORIGINS = ['https://' + os.environ.get('RAILWAY_STATIC_URL', '.railway.app')]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Required for sitemaps
    'django.contrib.sitemaps',  # Required for sitemaps
    'channels', # Django Channels
    'dashboard.apps.DashboardConfig', # Your app
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'dashboard.middleware.DatabaseHealthCheckMiddleware',  # Database health check
    'dashboard.enhanced_security.EnhancedSecurityMiddleware',  # Enhanced security
    'dashboard.enhanced_security.SecurityAuditMiddleware',  # Security audit logging
    'dashboard.enhanced_security.CSRFProtectionMiddleware',  # Enhanced CSRF protection
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'AquaGuard.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'dashboard/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
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
WSGI_APPLICATION = 'AquaGuard.wsgi.application'

# --- PRODUCTION DATABASE CONFIGURATION ---
# Check for Railway PostgreSQL service first
RAILWAY_DATABASE_URL = os.environ.get('RAILWAY_DATABASE_URL')
if RAILWAY_DATABASE_URL:
    print("Found RAILWAY_DATABASE_URL environment variable.")
    DATABASES = {
        'default': dj_database_url.parse(RAILWAY_DATABASE_URL, conn_max_age=600)
    }
    DATABASES['default']['OPTIONS'] = {
        'sslmode': 'require',
        'connect_timeout': 10,  # Wait up to 10 seconds for connection
        'options': '-c statement_timeout=30000'  # 30 second query timeout
    }
    # Add connection pooling settings for better reliability
    DATABASES['default']['CONN_MAX_AGE'] = 600  # Keep connections alive for 10 minutes
else:
    DATABASE_URL_FROM_ENV = os.environ.get('DATABASE_URL')
    if DATABASE_URL_FROM_ENV:
        print("Found DATABASE_URL environment variable.") # Add this line for logging
        DATABASES = {
            'default': dj_database_url.parse(DATABASE_URL_FROM_ENV, conn_max_age=600)
        }
        DATABASES['default']['OPTIONS'] = {
            'sslmode': 'require',
            'connect_timeout': 10,  # Wait up to 10 seconds for connection
            'options': '-c statement_timeout=30000'  # 30 second query timeout
        }
        # Add connection pooling settings for better reliability
        DATABASES['default']['CONN_MAX_AGE'] = 600  # Keep connections alive for 10 minutes
    else:
        print("WARNING: DATABASE_URL environment variable not found or empty. Using local fallback.") # Add this line for logging
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'AquaGuard_db',
                'USER': 'postgres',
                'PASSWORD': os.environ.get('DB_PASSWORD', ''),
                'HOST': 'localhost',
                'PORT': '5432',
                'CONN_MAX_AGE': 600,  # Keep connections alive for 10 minutes
                'OPTIONS': {
                    'connect_timeout': 10,  # Wait up to 10 seconds for connection
                    'options': '-c statement_timeout=30000'  # 30 second query timeout
                }
            }
        }
    # Verify database configuration
    if not DATABASES['default'].get('ENGINE'):
        raise ImproperlyConfigured("Database settings are not configured. DATABASE_URL env var is missing and fallback failed.")
    
    # Security check: Ensure no hardcoded passwords
    if not os.environ.get('DB_PASSWORD') and not DATABASE_URL_FROM_ENV:
        print("WARNING: DB_PASSWORD not set, using empty password for local development")
        # For Railway deployment, we'll use DATABASE_URL instead


# Password validation moved to Enhanced Security Settings below

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (WhiteNoise)
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'dashboard/static')]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Channels Configuration (UPDATED) ---
ASGI_APPLICATION = 'AquaGuard.asgi.application'
# **Use Redis for production channel layer**
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379') # Get Redis URL from env vars
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [REDIS_URL],
        },
    },
}

# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 900
SESSION_SAVE_EVERY_REQUEST = True

# Authentication URLs
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'device_list'
LOGOUT_REDIRECT_URL = 'public_home' # <-- **CHANGED**

# ... (Keep ENHANCED SECURITY SETTINGS as they were) ...
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SAMESITE = 'Lax'
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIF = True
X_FRAME_OPTIONS = 'DENY'
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Firebase Admin SDK Configuration - Environment Variables Only
FIREBASE_CREDENTIALS = os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON', '')
# Firebase Configuration - Use environment variables for security
FIREBASE_API_KEY = os.environ.get('FIREBASE_API_KEY', '')
FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID', '')
FIREBASE_MESSAGING_SENDER_ID = os.environ.get('FIREBASE_MESSAGING_SENDER_ID', '')
FIREBASE_APP_ID = os.environ.get('FIREBASE_APP_ID', '')
VAPID_PUBLIC_KEY = os.environ.get('VAPID_PUBLIC_KEY', '')

# Site ID for sitemaps (required for Django sitemaps)
SITE_ID = 1

# --- ENHANCED SECURITY SETTINGS ---
# Custom admin URL for security
ADMIN_URL = os.environ.get('ADMIN_URL', 'AquaSavvy-Control/')

# Enhanced password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,  # Increased minimum length
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'OPTIONS': {
            'user_attributes': ('username', 'email', 'first_name', 'last_name'),
            'max_similarity': 0.7,
        }
    },
]

# Enhanced session security
SESSION_COOKIE_AGE = 1800  # 30 minutes
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SAMESITE = 'Strict'

# Enhanced CSRF security
CSRF_COOKIE_HTTPONLY = False  # Must be False for AJAX
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_USE_SESSIONS = True
CSRF_FAILURE_VIEW = 'dashboard.views.csrf_failure_view'

# Enhanced security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Production security settings
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Rate limiting settings
RATE_LIMIT_ENABLED = True
RATE_LIMIT_REQUESTS_PER_MINUTE = 60
RATE_LIMIT_LOGIN_ATTEMPTS = 5
RATE_LIMIT_LOGIN_WINDOW = 300  # 5 minutes