import os

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

if os.getenv("USE_GUNICORN", "true").lower() in ("false", "0"):
    USE_MINIO = False
    STATIC_URL = "/static/"
    MEDIA_URL = "/media/"
    STATIC_ROOT = os.path.join("/jandig", "static")
    MEDIA_ROOT = os.path.join("/jandig", "media")
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

if os.getenv("USE_GUNICORN", "true").lower() in ("true", "1"):
    STORAGES = {
        "default": {
            "BACKEND": "config.storage_backends.PublicMediaStorage",
        },
        "staticfiles": {
            "BACKEND": "config.storage_backends.StaticStorage",
        },
    }
