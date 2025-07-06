import logging
import os
import re
import sys
from datetime import timedelta
from socket import gethostbyname, gethostname

import environ
import sentry_sdk
from django.utils.translation import gettext_lazy as _
from sentry_sdk.integrations.django import DjangoIntegration

ROOT_DIR = environ.Path(__file__) - 3  # three folders back (/jandig/src/config)
BASE_DIR = ROOT_DIR.path("src")

env = environ.Env()

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(str(ROOT_DIR.path(".env")))

DEBUG = env.bool("DJANGO_DEBUG", False)

CSRF_TRUSTED_ORIGINS = ["https://*.jandig.app"]


SECRET_KEY = env("DJANGO_SECRET_KEY")

ALLOWED_HOSTS = [
    "localhost",
    "0.0.0.0",
    "127.0.0.1",
    gethostname(),
    gethostbyname(gethostname()),
]
CUSTOM_ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["*"])
ALLOWED_HOSTS += CUSTOM_ALLOWED_HOSTS


DJANGO_ADMIN_URL = env("DJANGO_ADMIN_URL", default="admin/")
# Sentry configuration
ENABLE_SENTRY = env("ENABLE_SENTRY", default=False)
HEALTH_CHECK_URL = env("HEALTH_CHECK_URL", default="api/v1/status/")
SENTRY_TRACES_SAMPLE_RATE = env("SENTRY_TRACES_SAMPLE_RATE", default=0.1)
SENTRY_PROFILES_SAMPLE_RATE = env("SENTRY_PROFILES_SAMPLE_RATE", default=0.1)
SENTRY_ENVIRONMENT = env("SENTRY_ENVIRONMENT", default="")
SENTRY_RELEASE = env("SENTRY_RELEASE", default="1.5.5")


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
        environment=SENTRY_ENVIRONMENT,
        integrations=[DjangoIntegration()],
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
        traces_sampler=traces_sampler,
        profiles_sample_rate=SENTRY_PROFILES_SAMPLE_RATE,
        release=SENTRY_RELEASE,
    )

INSTALLED_APPS = [
    "pghistory.admin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "pghistory",
    "pgtrigger",
    "django_htmx",
    "corsheaders",
    "users",
    "core",
    "blog",
]

DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": "config.settings.debug"}
TOOLBAR_ENABLED = env.bool("DEBUG_TOOLBAR", False)


def debug(_):
    return TOOLBAR_ENABLED


MIDDLEWARE = []

if TOOLBAR_ENABLED:
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

MIDDLEWARE += [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

ROOT_URLCONF = "config.urls"

PAGE_SIZE = 20

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": PAGE_SIZE,
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
}
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "TOKEN_OBTAIN_SERIALIZER": "users.serializers.JandigJWTSerializer",
}
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "environment": "config.jinja2.environment",
        },
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

USE_POSTGRES = env.bool("USE_POSTGRES", default=True)
if USE_POSTGRES:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "HOST": env("POSTGRES_HOST", default="localhost"),
            "NAME": env("POSTGRES_DB", default="jandig"),
            "USER": env("POSTGRES_USER", default="jandig"),
            "PASSWORD": env("POSTGRES_PASSWORD", default="secret"),
        },
        "OPTIONS": {
            "pool": True,
        },
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(ROOT_DIR, "db.sqlite3"),
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOCALE_PATHS = (os.path.join(str(ROOT_DIR), "locale"),)

LANGUAGE_CODE = "en"

LANGUAGES = (
    ("en-us", _("English")),
    ("pt-br", _("Brazilian Portuguese")),
    ("es-es", _("European Spanish")),
)

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# LOGIN / LOGOUT
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

# Sphinx docs
DOCS_ROOT = "/jandig/build/"


DEFAULT_FROM_EMAIL = env("SMTP_SENDER_MAIL", default="jandig@memelab.com.br")
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("SMTP_SERVER", default="mailpit")
EMAIL_USE_TLS = env("SMTP_USE_TLS", default=False)
EMAIL_PORT = env("SMTP_PORT", default=1025)
EMAIL_HOST_USER = env("SMTP_USER", default="jandig@jandig.com")
EMAIL_HOST_PASSWORD = env("SMTP_PASSWORD", default="password")
EMAIL_USE_SSL = False

# Recaptcha
RECAPTCHA_ENABLED = env("RECAPTCHA_ENABLED", default=False)
RECAPTCHA_SITE_KEY = env("RECAPTCHA_SITE_KEY", default="")
RECAPTCHA_PROJECT_ID = env("RECAPTCHA_PROJECT_ID", default="")
RECAPTCHA_GCLOUD_API_KEY = env("RECAPTCHA_GCLOUD_API_KEY", default="")

###########################
#### Storage settings  ####
###########################
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME", "")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "us-east-2")
AWS_DEFAULT_ACL = os.getenv("AWS_DEFAULT_ACL", None)
AWS_STATIC_LOCATION = os.getenv("AWS_STATIC_LOCATION", "static")
AWS_MEDIA_LOCATION = os.getenv("AWS_MEDIA_LOCATION", "media")

USE_GUNICORN = os.getenv("USE_GUNICORN", "true").lower() in ("true", "1")

if not USE_GUNICORN:
    USE_MINIO = False
    STATIC_URL = "/static/"
    MEDIA_URL = "/media/"
    STATIC_ROOT = os.path.join(ROOT_DIR, "static")
    MEDIA_ROOT = os.path.join(ROOT_DIR, "media")
else:
    USE_MINIO = os.getenv("USE_MINIO", False)

if USE_MINIO:
    AWS_S3_ENDPOINT_URL = os.getenv("MINIO_S3_ENDPOINT_URL", "http://storage:9000")
    AWS_S3_CUSTOM_DOMAIN = f"localhost:9000/{AWS_STORAGE_BUCKET_NAME}"
    AWS_S3_USE_SSL = False
    AWS_S3_SECURE_URLS = False
    AWS_S3_URL_PROTOCOL = "http:"

else:
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
    AWS_S3_URL_PROTOCOL = "https:"

# Static configuration
# Add your own apps statics in this list
BASE_SRC_PATH = "/jandig/src"
STATICFILES_DIRS = [
    os.path.join(BASE_SRC_PATH, "core", "static"),
    os.path.join(BASE_SRC_PATH, "users", "static"),
    os.path.join(BASE_SRC_PATH, "blog", "static"),
]

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

AWS_PUBLIC_MEDIA_LOCATION = "media/public"

if USE_GUNICORN:
    STORAGES = {
        "default": {
            "BACKEND": "config.storage_backends.PublicMediaStorage",
        },
        "staticfiles": {
            "BACKEND": "config.storage_backends.StaticStorage",
        },
    }


if len(sys.argv) > 1 and sys.argv[1] == "test":
    logging.disable(logging.CRITICAL)
