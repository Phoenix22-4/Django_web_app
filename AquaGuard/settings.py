from pathlib import Path
import os
import dj_database_url # We keep this for local fallback

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- SECURITY CHANGE FOR AWS ---
# In production, this will be read from an environment variable in Elastic Beanstalk
SECRET_KEY = os.environ.get('SECRET_KEY', 'a-default-secret-key-for-local-dev')

# --- DEPLOYMENT CHANGE FOR AWS ---
# DEBUG is always False on a live server
DEBUG = False

# --- DEPLOYMENT CHANGE FOR AWS ---
# Reads the automatically provided hostname from Elastic Beanstalk
ALLOWED_HOSTS = [os.environ.get('EB_HOSTNAME', 'localhost')]

# --- DEPLOYMENT CHANGE FOR AWS ---
# A security setting required for live HTTPS sites
CSRF_TRUSTED_ORIGINS = [f"https://{os.environ.get('EB_HOSTNAME')}"] if 'EB_HOSTNAME' in os.environ else []


# Application definition
INSTALLED_APPS = [
    'daphne', # Daphne must be the first app
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
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


# --- DEPLOYMENT CHANGE FOR AWS ---
# This configuration reads the database credentials from the environment
# variables that Elastic Beanstalk automatically provides for your RDS database.
DB_NAME = os.environ.get('RDS_DB_NAME')
DB_USER = os.environ.get('RDS_USERNAME')
DB_PASSWORD = os.environ.get('RDS_PASSWORD')
DB_HOST = os.environ.get('RDS_HOSTNAME')
DB_PORT = os.environ.get('RDS_PORT')

# Check if we are on AWS. If so, use the RDS database.
IS_AWS_ENVIRONMENT = all([DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT])

if IS_AWS_ENVIRONMENT:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': DB_NAME,
            'USER': DB_USER,
            'PASSWORD': DB_PASSWORD,
            'HOST': DB_HOST,
            'PORT': DB_PORT,
        }
    }
else:
    # Fallback to your local PostgreSQL database if not on AWS
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'AquaGuard_db',
            'USER': 'postgres',
            'PASSWORD': 'mwamboa22#',
            'HOST': 'localhost',
            'PORT': '5432',
        }
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
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') # This is needed for Elastic Beanstalk
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


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
