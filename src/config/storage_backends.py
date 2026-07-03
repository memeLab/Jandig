from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
from storages.backends.s3boto3 import S3ManifestStaticStorage as BaseManifestStaticStorage
from storages.backends.s3boto3 import S3StaticStorage


class StaticStorage(S3StaticStorage):
    location = settings.AWS_STATIC_LOCATION


class ManifestStaticStorage(BaseManifestStaticStorage):
    location = settings.AWS_STATIC_LOCATION

    def get_object_parameters(self, name):
        params = super().get_object_parameters(name)
        params["CacheControl"] = "max-age=31536000"
        return params


class PublicMediaStorage(S3Boto3Storage):
    location = settings.AWS_PUBLIC_MEDIA_LOCATION
    file_overwrite = False
