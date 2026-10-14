import logging

from PIL import Image

log = logging.getLogger(__name__)


def extract_dimensions(file, extension, thumbnail=None):
    """Extract width and height from a media file.

    Args:
        file: A file-like object (Django FieldFile, InMemoryUploadedFile, etc.)
        extension: The file extension (gif, png, mp4, webm, glb)
        thumbnail: Optional thumbnail file for GLB objects

    Returns:
        A tuple (width, height) or None if extraction fails.
    """
    try:
        if extension in ("png", "gif"):
            return _dimensions_from_image(file)
        elif extension in ("mp4", "webm"):
            return _dimensions_from_video(file)
        elif extension == "glb":
            if thumbnail:
                return _dimensions_from_image(thumbnail)
            return None
    except Exception:
        log.exception("Failed to extract dimensions for %s file", extension)
        return None


def _dimensions_from_image(file):
    """Extract dimensions from an image file using Pillow."""
    pos = file.tell() if hasattr(file, "tell") else 0
    try:
        img = Image.open(file)
        width, height = img.size
        return (width, height)
    finally:
        if hasattr(file, "seek"):
            file.seek(pos)


def _dimensions_from_video(file):
    """Extract dimensions from a video file using PyAV."""
    import av

    pos = file.tell() if hasattr(file, "tell") else 0
    try:
        container = av.open(file)
        try:
            stream = container.streams.video[0]
            return (stream.width, stream.height)
        finally:
            container.close()
    finally:
        if hasattr(file, "seek"):
            file.seek(pos)
