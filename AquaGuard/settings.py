# AquaGuard/settings.py
from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-fallback-for-local-dev')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

RAILWAY_HOST = os.environ.get('RAILWAY_STATIC_URL')
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
if RAILWAY_HOST:
    ALLOWED_HOSTS.append(RAILWAY_HOST)

CSRF_TRUSTED_ORIGINS = []
if RAILWAY_HOST:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RAILWAY_HOST}")
if DEBUG:
    CSRF_TRUSTED_ORIGINS.extend(['http://localhost:8000', 'http://127.0.0.1:8000'])

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

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'dashboard.middleware.DatabaseHealthCheckMiddleware',  # ✅ Your middleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'dashboard.enhanced_security.EnhancedSecurityMiddleware',  # ✅ Enhanced security
    'dashboard.enhanced_security.SecurityAuditMiddleware',    # ✅ Audit logging
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'AquaGuard.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'dashboard' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
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

# DATABASE
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=True)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'dashboard' / 'static']
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Channels & Redis
ASGI_APPLICATION = 'AquaGuard.asgi.application'
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {"hosts": [REDIS_URL]},
    },
}

# Caching (for rate limiting)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    }
}

# Sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1800
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SAMESITE = 'Lax'

# Auth
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'device_list'
LOGOUT_REDIRECT_URL = 'public_home'

# Firebase (env vars)
FIREBASE_CREDENTIALS = os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON', '')
FIREBASE_API_KEY = os.environ.get('FIREBASE_WEB_API_KEY', '')
FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID', '')
FIREBASE_MESSAGING_SENDER_ID = os.environ.get('FIREBASE_MESSAGING_SENDER_ID', '')
FIREBASE_APP_ID = os.environ.get('FIREBASE_WEB_APP_ID', '')
FIREBASE_MEASUREMENT_ID = os.environ.get('FIREBASE_MEASUREMENT_ID', '')
VAPID_PUBLIC_KEY = os.environ.get('VAPID_PUBLIC_KEY', '')

SITE_ID = 1
ADMIN_URL = os.environ.get('ADMIN_URL', 'admin/')

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# CSRF
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_FAILURE_VIEW = 'dashboard.views.csrf_failure_view'

# Production security
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Rate limiting settings
RATE_LIMIT_ENABLED = True
RATE_LIMIT_REQUESTS_PER_MINUTE = int(os.environ.get('RATE_LIMIT_REQUESTS_PER_MINUTE', 61))
RATE_LIMIT_LOGIN_ATTEMPTS = int(os.environ.get('RATE_LIMIT_LOGIN_ATTEMPTS', 5))
RATE_LIMIT_LOGIN_WINDOW = int(os.environ.get('RATE_LIMIT_LOGIN_WINDOW', 61))  # ✅ 61 seconds

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': 'INFO'},
    'loggers': {
        'django': {'handlers': ['console'], 'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'), 'propagate': False},
        'dashboard': {'handlers': ['console'], 'level': 'INFO', 'propagate': False}
    },
}