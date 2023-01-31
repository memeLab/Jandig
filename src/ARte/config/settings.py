import os
import environ
from .wait_db import start_services
from django.utils.translation import ugettext_lazy as _

from socket import gethostbyname, gethostname

ROOT_DIR = environ.Path(__file__) - 2  # (ARte/config/settings.py - 2 = ARte/)
APPS_DIR = ROOT_DIR.path('ARte')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = environ.Env()

READ_DOT_ENV_FILE = env.bool('DJANGO_READ_DOT_ENV_FILE', default=False)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(str(ROOT_DIR.path('.env')))

DEBUG = env.bool('DJANGO_DEBUG', False)


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('DJANGO_SECRET_KEY', default='gw)48fp(ct67v4+0_tpxl=$vw=-x&y9(&0n6!n4mpw5m!4gaor')

ALLOWED_HOSTS = [
    "localhost",
    "0.0.0.0",
    "127.0.0.1",
    gethostname(),
    gethostbyname(gethostname()),
]
CUSTOM_ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['*'])
ALLOWED_HOSTS += CUSTOM_ALLOWED_HOSTS
print(f"ALLOWED_HOSTS:{ALLOWED_HOSTS}")
# Application definition

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
import re

# Sentry configuration
ENABLE_SENTRY = env("ENABLE_SENTRY", default=False)
HEALTH_CHECK_URL = env("HEALTH_CHECK_URL", default="api/v1/status/")
SENTRY_TRACES_SAMPLE_RATE = env("SENTRY_TRACES_SAMPLE_RATE", default=0.1)
DJANGO_ADMIN_URL = env("DJANGO_ADMIN_URL", default="admin/")


def traces_sampler(sampling_context):
    url = sampling_context["wsgi_environ"]["PATH_INFO"]
    is_health_check = url == f"/{HEALTH_CHECK_URL}"
    is_django_admin = re.search(f"^/{DJANGO_ADMIN_URL.strip('/')}/*", url) is not None
    if is_health_check or is_django_admin:
        return 0
    return SENTRY_TRACES_SAMPLE_RATE


if ENABLE_SENTRY:
    SENTRY_DSN = env("SENTRY_DSN")
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
        traces_sampler=traces_sampler,
    )

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'debug_toolbar',
    'corsheaders',
    'users',
    'core',
    'docs',
    #'django_extensions',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': 'config.settings.debug'    
}

def debug(request):
    return env.bool('DEBUG_TOOLBAR', False)

## Let whitenoise serve static files  -- DON'T USE IN PRODUCTION --
if env.bool('DEV_STATIC', False):
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    print('\n ------- SERVING STATIC FILES USING WHITENOISE! -------\n')

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
     {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'environment': 'config.jinja2.environment',
        },
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'


if env.bool('DEV_DB', False):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'HOST': env('POSTGRES_HOST'),
            'NAME': env('POSTGRES_DB'),
            'USER': env('POSTGRES_USER'),
            'PASSWORD': env('POSTGRES_PASSWORD'),
        },
    }

    # STARTS SERVICES THAT DJANGO DEPENDS E.G. postgres
    start_services()


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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LOCALE_PATHS = (
    # os.path.join(str(ROOT_DIR), 'locale'),
    '/ARte/locale',
)

LANGUAGE_CODE = 'en'

LANGUAGES = (
    ('en-us', _('English')),
    ('pt-br', _('Brazilian Portuguese')),
)

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

COLLECT_DIR = os.path.dirname(os.path.dirname(BASE_DIR))
USE_S3 = os.getenv("USE_S3", "False").lower() == "true"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'core', 'static'),
    os.path.join(BASE_DIR, 'users', 'static')
]
if USE_S3:
    # AWS credentials
    AWS_S3_OBJECT_PARAMETERS = {
        "CacheControl": "max-age=86400",
    }
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME", "")
    AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "us-east-2")
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
    AWS_DEFAULT_ACL = os.getenv("AWS_DEFAULT_ACL", None)
    AWS_STATIC_LOCATION = os.getenv("AWS_STATIC_LOCATION", "static")

    # Static configuration
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_STATIC_LOCATION}/"
    STATICFILES_STORAGE = "config.storage_backends.StaticStorage"

    AWS_PUBLIC_MEDIA_LOCATION = "media/public"
    DEFAULT_FILE_STORAGE = "config.storage_backends.PublicMediaStorage"
else:
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(COLLECT_DIR, 'collect')
 

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'users', 'media')

# LOGIN / LOGOUT
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# Sphinx docs
DOCS_ROOT = os.path.join(BASE_DIR, '../../build/')