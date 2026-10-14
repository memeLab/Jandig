import io
import os

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


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


SQUARE_SVG = b"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
  <rect width="100" height="100" fill="white"/>
  <circle cx="50" cy="50" r="30" fill="black"/>
</svg>
"""


def svg_upload(name="marker.svg", content=SQUARE_SVG):
    return SimpleUploadedFile(name, content, content_type="image/svg+xml")


def gif_upload(name="marker.gif"):
    buffer = io.BytesIO()
    Image.new("P", (200, 200), 0).save(buffer, format="GIF")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/gif")


# Smallest PDF that is still a valid document; Pillow can write PDFs but not
# read them, so this must be turned away like any other non-image.
MINIMAL_PDF = (
    b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Kids[]/Count 0>>endobj\n"
    b"trailer<</Root 1 0 R>>\n%%EOF\n"
)


def pdf_upload(name="marker.pdf"):
    return SimpleUploadedFile(name, MINIMAL_PDF, content_type="application/pdf")


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
