import os

from django.conf import settings
from django.core.files.base import ContentFile


def get_example_object(filename):
    return ContentFile(
        open(
            os.path.join(
                os.path.join(settings.ROOT_DIR + "collection/", "objects/"),
                filename,
            ),
            "rb",
        ).read(),
        name=filename,
    )


def get_example_sound(filename):
    return ContentFile(
        open(
            os.path.join(
                os.path.join(settings.ROOT_DIR + "collection/", "sounds/"),
                filename,
            ),
            "rb",
        ).read(),
        name=filename,
    )
