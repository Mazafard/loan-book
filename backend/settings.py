import datetime
import os

import django.utils.encoding
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from corsheaders.defaults import default_headers
from six import python_2_unicode_compatible

django.utils.encoding.python_2_unicode_compatible = python_2_unicode_compatible

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('_SECRET_KEY', '$ia==gdfdgg)p7yp5w-gp2kdmdfgddgn8f&p$dj!!f%p3ypdx4()@mq@dgdfgji!0ao')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(os.getenv('_DEBUG', '1')))

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'jet.dashboard',
    'jet',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'corsheaders',
    'drf_yasg',

    'common',
    'service',

    'book',
    'users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME', 'rent_book'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASS', 'postgres'),
        'HOST': os.environ.get('DB_HOST', '0.0.0.0'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
# STATIC_URL = '/static/'
STATIC_ROOT = 'static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static_files"),
]
STATIC_URL = '/static_backend/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

CRISPY_TEMPLATE_PACK = 'bootstrap4'
CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_HEADERS = default_headers + (
    "X-Pagination-Total-Count",
    "X-Pagination-Page-Count",
    "X-Pagination-Current-Page",
    "X-Pagination-Per-Page",
    "X-Pagination-Sortable-Fields",
    "X-Pagination-Filterable-Fields",
    "X-Pagination-Searchable-Fields",
    "X-University-Domain",
    "Link",
    "x-locale",
    "x-currency",
    "Accepted-language",
)

CORS_EXPOSE_HEADERS = (
    "X-Pagination-Total-Count",
    "X-Pagination-Page-Count",
    "X-Pagination-Current-Page",
    "X-Pagination-Per-Page",
    "X-Pagination-Sortable-Fields",
    "X-Pagination-Filterable-Fields",
    "X-Pagination-Searchable-Fields",
    "Link",
    "x-locale",
    "x-currency",
    "Accepted-language",
)

DEFAULT_PAGINATION_PAGE_SIZE = 10

SMS_RESEND_WAITE_TIME = 60
SMS_CODE_EXPIRE_TIME = 60 * 10
SMS_CODE_LENGTH = 5
SMS_MAX_TRY_COUNT = 5
EMAIL_VERIFICATION_CODE_SIZE = 128

BROKER_TRANSPORT = os.getenv("_BROKER_TRANSPORT", "redis")
BROKER_HOST = os.getenv("_BROKER_HOST", "127.0.0.1")
BROKER_PORT = int(os.getenv("_BROKER_PORT", "6379"))
BROKER_VHOST = int(os.getenv("_BROKER_VHOST", "2"))
CELERY_BROKER = "{}://{}:{}/{}".format(BROKER_TRANSPORT, BROKER_HOST,
                                       BROKER_PORT, BROKER_VHOST)

JWT_AUTH = {
    'JWT_ENCODE_HANDLER':
        'rest_framework_jwt.utils.jwt_encode_handler',

    'JWT_DECODE_HANDLER':
        'rest_framework_jwt.utils.jwt_decode_handler',

    'JWT_PAYLOAD_HANDLER':
        'rest_framework_jwt.utils.jwt_payload_handler',

    'JWT_PAYLOAD_GET_USER_ID_HANDLER':
        'rest_framework_jwt.utils.jwt_get_user_id_from_payload_handler',

    'JWT_RESPONSE_PAYLOAD_HANDLER':
        'rest_framework_jwt.utils.jwt_response_payload_handler',

    'JWT_SECRET_KEY': SECRET_KEY,
    'JWT_GET_USER_SECRET_KEY': None,
    'JWT_PUBLIC_KEY': None,
    'JWT_PRIVATE_KEY': None,
    'JWT_ALGORITHM': 'HS256',
    'JWT_VERIFY': True,
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_LEEWAY': 0,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=30),
    'JWT_AUDIENCE': None,
    'JWT_ISSUER': None,

    'JWT_ALLOW_REFRESH': True,
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=365),

    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
    'JWT_AUTH_COOKIE': None,
}

UPLOAD_DIRECTORY = os.getenv('_UPLOAD_DIRECTORY', 'uploads/')
CDN_DOMAIN = os.getenv('_CDN_DOMAIN', '/uploads/')
JET_SIDE_MENU_COMPACT = True

EMAIL_HOST = os.getenv('_EMAIL_HOST', '')
EMAIL_PORT = os.getenv('_EMAIL_PORT', '25')
EMAIL_HOST_USER = os.getenv('_EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('_EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = bool(int(os.getenv('_EMAIL_USE_TLS', '0')))
EMAIL_USE_SSL = bool(int(os.getenv('_EMAIL_USE_SSL', '0')))
SYSTEM_MAIL_FROM = os.getenv('_SYSTEM_MAIL_FROM', EMAIL_HOST_USER)

APPLICATION_BASE_URL = os.getenv('_APPLICATION_BASE_URL', 'http://127.0.0.1:8000')
WEBSITE_URL = os.getenv('_WEBSITE_URL', '')

REDIS_CACHE_DB = int(os.getenv("_REDIS_CACHE_DB", "0"))

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "{}://{}:{}/{}".format(BROKER_TRANSPORT, BROKER_HOST,
                                           BROKER_PORT, REDIS_CACHE_DB),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
        "KEY_PREFIX": "service"
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

SWAGGER_SETTINGS = {
    'SHOW_REQUEST_HEADERS': True,

    'VALIDATOR_URL': 'http://localhost:8090',

    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'SUPPORTED_SUBMIT_METHODS': [
        'get',
        'post',
        'put',
        'delete',
        'patch'
    ],
}
# Import local settings in case they exist
try:
    from backend.settings_local import *
except ImportError:
    pass
