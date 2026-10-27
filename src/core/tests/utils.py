import base64
import io
import math
import os
import struct
import zlib

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


def svg_document(body):
    """A 100x100 SVG on a white background with body (SVG markup) on top."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">'
        f'<rect width="100" height="100" fill="white"/>{body}</svg>'
    ).encode()


def data_url(content, mime):
    return f"data:{mime};base64,{base64.b64encode(content).decode()}"


def svg_with_image(content, mime="image/png", copies=1):
    """An SVG that draws content, as a data: URL, over its whole area."""
    image = f'<image href="{data_url(content, mime)}" width="100" height="100"/>'
    return svg_document(image * copies)


def png_bytes(width, height):
    """A black PNG of any size, written by hand in 1-bit greyscale so that it
    costs only its compressed bytes here; Pillow would hold the whole image in
    memory to save it. Whatever decodes it allocates the full size."""

    def chunk(kind, data):
        checksum = zlib.crc32(kind + data)
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", checksum)

    row = b"\x00" + bytes(math.ceil(width / 8))  # filter byte, then black pixels
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 1, 0, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(row * height))
        + chunk(b"IEND", b"")
    )


def raster_image_bytes(image_format, size=(10, 10)):
    buffer = io.BytesIO()
    Image.new("L", size, 0).save(buffer, format=image_format)
    return buffer.getvalue()
