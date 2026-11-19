import os

from django.conf import settings
from django.core.asgi import get_asgi_application

from config.request_limits import RequestBodyLimitMiddleware

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = RequestBodyLimitMiddleware(
    get_asgi_application(), max_size=settings.MAX_REQUEST_BODY_SIZE
)
