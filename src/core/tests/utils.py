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


def make_svg(width=None, height=None, viewbox=None):
    """An SVG of a black circle, sized by whichever of width, height and
    viewBox are given (each may carry units, e.g. "1in")."""
    attributes = "".join(
        f' {name}="{value}"'
        for name, value in (
            ("width", width),
            ("height", height),
            ("viewBox", viewbox),
        )
        if value is not None
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg"{attributes}>'
        '<rect width="100%" height="100%" fill="white"/>'
        '<circle cx="50%" cy="50%" r="30%" fill="black"/></svg>'
    ).encode()
