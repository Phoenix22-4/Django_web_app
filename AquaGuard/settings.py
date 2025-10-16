# AquaGuard/settings.py
from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# --- PRODUCTION SETTINGS ---
# Secret key is read from an environment variable
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-fallback-for-local-dev')

# DEBUG is False in production, unless an env var says otherwise
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Allow the domain Railway will assign to your app
ALLOWED_HOSTS = [os.environ.get('RAILWAY_STATIC_URL', '.railway.app')]

# --- ADD THIS LINE FOR CSRF FIX ---
CSRF_TRUSTED_ORIGINS = ['https://' + os.environ.get('RAILWAY_STATIC_URL', '.railway.app')]

# --- ADD THIS COMMENT ---
# Triggering a new deployment to run the release phase.

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'push_notifications',
    'dashboard.apps.DashboardConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
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
            ],
        },
    },
]
WSGI_APPLICATION = 'AquaGuard.wsgi.application'

# --- PRODUCTION DATABASE CONFIGURATION ---
DATABASES = {
    'default': dj_database_url.config(
        # Fallback to your local Postgres database if DATABASE_URL is not set
        default='postgresql://postgres:mwamboa22%23@localhost:5432/AquaGuard_db',
        conn_max_age=600
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'dashboard/static'),
]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
ASGI_APPLICATION = 'AquaGuard.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

SESSION_COOKIE_AGE = 900
SESSION_SAVE_EVERY_REQUEST = True

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'device_list'
LOGOUT_REDIRECT_URL = 'login'

# ==================== ENHANCED SECURITY SETTINGS ====================
# Prevent session hijacking
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG  # True in production (HTTPS only)
SESSION_COOKIE_SAMESITE = 'Lax'

# CSRF Protection
CSRF_COOKIE_HTTPONLY = False  # Must be False for AJAX to read it
CSRF_COOKIE_SECURE = not DEBUG  # True in production
CSRF_COOKIE_SAMESITE = 'Lax'

# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Force HTTPS in production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Password validation (already present, but ensure it's strong)
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==================== FIREBASE CLOUD MESSAGING (FCM) SETTINGS ====================
# For django-push-notifications
PUSH_NOTIFICATIONS_SETTINGS = {
    "FCM_API_KEY": os.environ.get('FCM_SERVER_KEY', ''),  # Firebase Cloud Messaging Server Key
    "WP_PRIVATE_KEY": os.environ.get('VAPID_PRIVATE_KEY', ''),
    "WP_CLAIMS": {"sub": "mailto:contact:vision072025@gmail.com"}
}

# Web Push VAPID keys (for push_handler.js)
# Public key is in push_handler.js: BMLnBIiNgOMINbDOGA24NWnufsGSMP9GF-Z12V8dbEXA8NwBy-UFPOrF8kDpGdVjeIQsMRE-oxf-y60W1p4DEcY