import os
import dj_database_url
import django_heroku
from pathlib import Path
from django.urls import reverse_lazy
from django.contrib.messages import constants as messages
from django.core.management.utils import get_random_secret_key

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False") == "1"

DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "False") == "1"

ALLOWED_HOSTS = ['plannit-app-348a63e69fce.herokuapp.com', 'localhost']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'import_export',
    'crispy_forms',    
    'debug_toolbar',
    'django_filters',
    'formtools',
    'rest_framework',
    'rest_framework.authtoken',
    'invitations',
    'django_summernote',
    'django_celery_beat',
    'storages',
    
    'dashboard',
    'tools',
    'notifications',
    'panel_carga',
    'bandeja_es',
    'configuracion',
    'buscador',
    'status',
    'status_encargado',
    'analitica',
]

SITE_ID = 3

CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Allauth methods
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = True

LOGIN_URL = reverse_lazy("account_login")

CELERY_TIMEZONE = 'America/Santiago'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

APPEND_SLASH = False

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ]
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'dmp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR.joinpath('templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
        },
    },
]

INTERNAL_IPS = [
    '127.0.0.1',
]

# EMAIL SETTINGS
EMAIL_HOST = 'mail.stod.cl'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'plannit@stod.cl')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'plannit@stod.cl'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

WSGI_APPLICATION = 'dmp.wsgi.application'

# Database
if DEVELOPMENT_MODE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'PLANNIT-DEV',
            'USER': 'postgres',
            'PASSWORD': 'dmp.2020',
            'HOST': os.getenv("DATABASE_URL", "134.209.78.27"),
            'PORT': 5432,
            'SSLMODE': 'require',
            'DISABLE_SERVER_SIDE_CURSORS': True,
        }
    }
else:
    DATABASES = {
        'default': dj_database_url.config(
            default=os.getenv('DATABASE_URL')
        )
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'es'
_ = lambda s: s

LANGUAGES = (
    ('es', _('Español')),
    ('zh', _('Chinese')),
    ('en', _('English')),
)

TIME_ZONE = 'America/Santiago'

USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATICFILES_DIRS = (BASE_DIR / 'static',)

USE_SPACES = os.getenv("USE_SPACES", "0") == "1"
if USE_SPACES:
    from .cdn.conf import *
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    STATIC_URL = '/static/'
    MEDIA_ROOT = BASE_DIR / 'static/media'
    MEDIA_URL = '/media/'
else:
    STATIC_URL = '/static/'
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'static/media'

MESSAGE_TAGS = {
    messages.DEBUG: 'alert alert-bordered alert-info',
    messages.INFO: 'alert alert-bordered alert-info',
    messages.SUCCESS: 'alert alert-bordered alert-success',
    messages.WARNING: 'alert alert-bordered alert-warning',
    messages.ERROR: 'alert alert-bordered alert-danger',
}

# Summernote
SUMMERNOTE_CONFIG = {
    'iframe': False,
    'summernote': {
        'airMode': False,
        'width': '100%',
        'height': '480',
        'lang': 'es-ES',
        'toolbar': [
            ['style', ['style']],
            ['font', ['bold', 'underline', 'clear']],
            ['fontname', ['fontname']],
            ['color', ['color']],
            ['para', ['ul', 'ol', 'paragraph']],
            ['table', ['table']],
            ['view', ['fullscreen', 'codeview', 'help']],
        ],
        'print': {
            'stylesheetUrl': '/some_static_folder/printable.css',
        },
        'codemirror': {
            'mode': 'htmlmixed',
            'lineNumbers': 'true',
            'theme': 'monokai',
        },
    },
    'attachment_require_authentication': True,
    'disable_attachment': False,
    'attachment_absolute_uri': False,
}

# Activate Django-Heroku.
django_heroku.settings(locals())
