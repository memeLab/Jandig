"""Byte-size limits for uploaded files (#1010).

The limits live in settings (``MAX_*_UPLOAD_SIZE``) so each deployment can
override them. They are checked with ``file.size`` before the file is read or
parsed, so an oversized upload never reaches Pillow, cairosvg or the storage
backend. Only fresh uploads are checked: editing without replacing the file
hands back the stored file, which may predate the limits.
"""

import math

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.utils.translation import gettext_lazy as _

KB = 1024
MB = 1024 * KB

SVG_MARKER = "svg_marker"
RASTER_MARKER = "raster_marker"
IMAGE_OBJECT = "image_object"
VIDEO_OBJECT = "video_object"
GLB_OBJECT = "glb_object"
AUDIO = "audio"
THUMBNAIL = "thumbnail"

# Each kind of upload maps to the setting holding its limit and the message
# shown when a file is over it.
_LIMITS = {
    SVG_MARKER: (
        "MAX_SVG_MARKER_UPLOAD_SIZE",
        _(
            "This file is %(size)s. SVG markers are limited to %(limit)s, so "
            "please simplify it, or export it as a PNG or JPG, before uploading."
        ),
    ),
    RASTER_MARKER: (
        "MAX_RASTER_MARKER_UPLOAD_SIZE",
        _(
            "This file is %(size)s. Marker images are limited to %(limit)s, so "
            "please resize or compress it before uploading."
        ),
    ),
    IMAGE_OBJECT: (
        "MAX_IMAGE_OBJECT_UPLOAD_SIZE",
        _(
            "This file is %(size)s. GIF and PNG objects are limited to "
            "%(limit)s, so please reduce its dimensions, colors or number of "
            "frames before uploading."
        ),
    ),
    VIDEO_OBJECT: (
        "MAX_VIDEO_OBJECT_UPLOAD_SIZE",
        _(
            "This file is %(size)s. MP4 and WebM videos are limited to "
            "%(limit)s, so please shorten or compress it before uploading."
        ),
    ),
    GLB_OBJECT: (
        "MAX_GLB_OBJECT_UPLOAD_SIZE",
        _(
            "This file is %(size)s. GLB models are limited to %(limit)s, so "
            "please optimize the model before uploading."
        ),
    ),
    AUDIO: (
        "MAX_AUDIO_UPLOAD_SIZE",
        _(
            "This file is %(size)s. Audio files are limited to %(limit)s, so "
            "please shorten or compress it (for example as MP3) before uploading."
        ),
    ),
    THUMBNAIL: (
        "MAX_THUMBNAIL_UPLOAD_SIZE",
        _(
            "The thumbnail generated for this model is %(size)s. Thumbnails are "
            "limited to %(limit)s, so please reload the page and upload the "
            "model again."
        ),
    ),
}

OBJECT_KIND_BY_EXTENSION = {
    "gif": IMAGE_OBJECT,
    "png": IMAGE_OBJECT,
    "mp4": VIDEO_OBJECT,
    "webm": VIDEO_OBJECT,
    "glb": GLB_OBJECT,
}


def format_size(num_bytes):
    """Human-readable size, rounded up so a file just over a limit never
    reads as equal to it."""
    for unit, factor in (("MB", MB), ("KB", KB)):
        if num_bytes >= factor:
            value = math.ceil(num_bytes * 10 / factor) / 10
            return f"{value:g} {unit}"
    return f"{num_bytes} B"


def upload_size_error(file, kind):
    """Return the error message if ``file`` is a fresh upload larger than the
    limit for ``kind``, or ``None`` if it is within the limit."""
    if not isinstance(file, UploadedFile):
        return None
    setting, message = _LIMITS[kind]
    limit = getattr(settings, setting)
    if file.size <= limit:
        return None
    return message % {"size": format_size(file.size), "limit": format_size(limit)}
