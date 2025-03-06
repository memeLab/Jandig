import logging
import os
import re
import sys
from socket import gethostbyname, gethostname

import environ
import sentry_sdk
from django.utils.translation import gettext_lazy as _
from sentry_sdk.integrations.django import DjangoIntegration

from .storage_settings import *  # noqa F403 F401

ROOT_DIR = environ.Path("/jandig/")
BASE_DIR = "/jandig/src"

env = environ.Env()

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(str(ROOT_DIR.path(".env")))

DEBUG = env.bool("DJANGO_DEBUG", False)

CSRF_TRUSTED_ORIGINS = ["https://*.jandig.app"]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("DJANGO_SECRET_KEY", default="change_me")

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
SENTRY_ENVIRONMENT = env("SENTRY_ENVIRONMENT", default="")
SENTRY_RELEASE = env("SENTRY_RELEASE", default="1.4.2")


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
        release=SENTRY_RELEASE,
    )


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "debug_toolbar",
    "django_htmx",
    "corsheaders",
    "users",
    "core",
    "blog",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
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
DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": "config.settings.debug"}


def debug(request):
    return env.bool("DEBUG_TOOLBAR", False)


ROOT_URLCONF = "config.urls"

PAGE_SIZE = 20

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": PAGE_SIZE,
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

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "HOST": env("POSTGRES_HOST", default="localhost"),
        "NAME": env("POSTGRES_DB", default="jandig"),
        "USER": env("POSTGRES_USER", default="jandig"),
        "PASSWORD": env("POSTGRES_PASSWORD", default="secret"),
    },
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

if len(sys.argv) > 1 and sys.argv[1] == "test":
    logging.disable(logging.CRITICAL)
