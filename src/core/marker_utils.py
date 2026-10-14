import logging
import math
from io import BytesIO
from types import SimpleNamespace

import cairosvg
from cairosvg.helpers import node_format
from cairosvg.parser import Tree
from django.core.exceptions import SuspiciousFileOperation
from django.core.files.base import ContentFile
from PIL import Image
from pymarker import generate_marker_from_image, remove_borders_from_image

log = logging.getLogger(__name__)

log = logging.getLogger(__name__)

BLACK_BORDER_PERCENTAGE = 20
WHITE_BORDER_PERCENTAGE = 3
INNER_BORDER_PERCENTAGE = 2

MARKER_SIZE = (256, 256)
SVG_RASTER_WIDTH = 1024  # px; the longest side of a rasterised SVG
# An SVG whose longest side is more than this many times its shortest side is
# rejected. pymarker squashes every image into a square the size of its
# shortest side, so at 10:1 the drawing is already compressed tenfold along
# its long side and the marker is built from a raster about 100px across;
# beyond that it degrades into a smear AR.js cannot tell apart from other
# markers, and at the far end the short side rounds down to zero pixels.
MAX_SVG_ASPECT_RATIO = 10
THUMB_SIZE = (128, 128)


def generate_marker_variants(marker, inner_border=False):
    storage = marker.source.storage

    with marker.source.open("rb") as f:
        original_image = Image.open(f)
        original_image.load()

    # Ensure RGB mode for consistent processing
    if original_image.mode == "RGBA":
        background = Image.new("RGB", original_image.size, (255, 255, 255))
        background.paste(original_image, mask=original_image.split()[3])
        original_image = background
    elif original_image.mode != "RGB":
        original_image = original_image.convert("RGB")

    ext = (
        marker.source.name.rsplit(".", 1)[-1].lower()
        if "." in marker.source.name
        else "png"
    )
    old_source_name = marker.source.name

    inner_border_percentage = INNER_BORDER_PERCENTAGE if inner_border else 0

    # 1. Save original at proper path
    original_blob = BytesIO()
    img_format = "JPEG" if ext in ("jpg", "jpeg") else "PNG"
    original_image.save(original_blob, img_format)
    original_path = f"markers/{marker.pk}/original.{ext}"
    _save_to_storage(storage, original_path, original_blob.getvalue())
    marker.source.name = original_path

    # 2. Generate marker image (black border only, resized to 256x256)
    marker_full = generate_marker_from_image(
        original_image,
        black_border_percentage=BLACK_BORDER_PERCENTAGE,
        white_border_percentage=0,
        inner_border_percentage=inner_border_percentage,
    )
    marker_resized = marker_full.resize(MARKER_SIZE, Image.LANCZOS)
    marker_blob = BytesIO()
    marker_resized.save(marker_blob, "PNG")
    marker_img_path = f"markers/{marker.pk}/marker.png"
    _save_to_storage(storage, marker_img_path, marker_blob.getvalue())
    marker.marker_img.name = marker_img_path

    # 3. Generate print image (black + white border, original size + borders)
    print_image = generate_marker_from_image(
        original_image,
        black_border_percentage=BLACK_BORDER_PERCENTAGE,
        white_border_percentage=WHITE_BORDER_PERCENTAGE,
        inner_border_percentage=inner_border_percentage,
    )
    print_blob = BytesIO()
    print_image.save(print_blob, "PNG")
    print_img_path = f"markers/{marker.pk}/print.png"
    _save_to_storage(storage, print_img_path, print_blob.getvalue())
    marker.print_img.name = print_img_path

    # 4. Generate thumbnail (128x128 from marker image)
    thumb_image = marker_full.resize(THUMB_SIZE, Image.LANCZOS)
    thumb_blob = BytesIO()
    thumb_image.save(thumb_blob, "PNG")
    thumb_img_path = f"markers/{marker.pk}/thumb.png"
    _save_to_storage(storage, thumb_img_path, thumb_blob.getvalue())
    marker.thumb_img.name = thumb_img_path

    # 5. Update file_size (size of print image for download reference)
    marker.file_size = len(print_blob.getvalue())

    # Save updated fields
    marker.save(
        update_fields=[
            "source",
            "marker_img",
            "print_img",
            "thumb_img",
            "file_size",
        ]
    )

    # Clean up the old source file if it moved to a new path.
    # This is not merely tidying: until it is gone, the object sits in public
    # storage under the name the uploader chose, so a failure here has to be
    # visible rather than swallowed. It still must not fail the upload.
    if old_source_name and old_source_name != marker.source.name:
        try:
            if storage.exists(old_source_name):
                storage.delete(old_source_name)
        except (OSError, SuspiciousFileOperation):
            log.exception(
                "Could not delete the pre-rename marker source %s for marker %s; "
                "it is still in storage under the uploader's own filename",
                old_source_name,
                marker.pk,
            )


def delete_marker_files(marker):
    """Delete all image files and the folder for a marker."""
    fields = [
        marker.source,
        marker.marker_img,
        marker.print_img,
        marker.thumb_img,
    ]
    for field in fields:
        try:
            field.delete(save=False)
        except Exception:
            pass


def _save_to_storage(storage, path, content_bytes):
    """Save content to storage, deleting any existing file at that path first."""
    try:
        if storage.exists(path):
            storage.delete(path)
    except Exception:
        pass
    storage.save(path, ContentFile(content_bytes))


def strip_existing_border(marker):
    """Remove a border the uploaded image already has, before generating ours.

    Without this, an image that is already a marker gets a second border drawn
    around the first one. Uses `FieldFile.save` rather than writing to storage
    directly, so the field's cached file handle is replaced — otherwise
    `generate_marker_variants` reopens the original upload and the strip is
    silently lost.

    The caller is expected to run `generate_marker_variants` afterwards, which
    moves the result to its canonical path and cleans up this intermediate.
    """
    with Image.open(marker.source) as image:
        stripped = remove_borders_from_image(image)
        blob = BytesIO()
        stripped.save(blob, "PNG")
    blob.seek(0)
    marker.source.save(
        f"markers/{marker.pk}/stripped.png", ContentFile(blob.getvalue()), save=True
    )


def is_svg(filename):
    return filename.lower().endswith(".svg")


class SvgAspectRatioError(ValueError):
    """The SVG is too long and thin to be usable as a marker."""


def svg_intrinsic_size(svg_bytes):
    """
    Return the (width, height) cairosvg would give the SVG, in px, without
    rendering it: the root's width and height, each falling back to the
    viewBox when missing or relative. Raises ValueError if the SVG cannot be
    parsed or has no usable size.
    """
    try:
        tree = Tree(bytestring=svg_bytes)
        # Mirrors the state cairosvg's own surface is in when it sizes the
        # root: 96 dpi, 12pt font, and no parent to resolve percentages against.
        surface = SimpleNamespace(
            context_width=None, context_height=None, dpi=96, font_size=16
        )
        width, height, _viewbox = node_format(surface, tree)
    except Exception as e:
        raise ValueError(f"Could not render SVG: {e}") from e
    if not all(math.isfinite(side) and side > 0 for side in (width, height)):
        raise ValueError("Could not render SVG: the SVG size is undefined")
    return width, height


def svg_raster_size(svg_bytes):
    """
    Return the (width, height) the SVG rasterises to: its intrinsic size
    scaled so the longest side is SVG_RASTER_WIDTH. Raises
    SvgAspectRatioError if the aspect ratio exceeds MAX_SVG_ASPECT_RATIO.
    """
    width, height = svg_intrinsic_size(svg_bytes)
    if max(width, height) / min(width, height) > MAX_SVG_ASPECT_RATIO:
        raise SvgAspectRatioError(
            f"SVG aspect ratio {width:g}x{height:g} exceeds {MAX_SVG_ASPECT_RATIO}:1"
        )
    scale = SVG_RASTER_WIDTH / max(width, height)
    return max(1, round(width * scale)), max(1, round(height * scale))


def rasterize_svg(svg_bytes):
    """
    Render an SVG to PNG bytes fitted within SVG_RASTER_WIDTH x
    SVG_RASTER_WIDTH, keeping its aspect ratio, the size the marker pipeline
    works from. Raises SvgAspectRatioError if the SVG is too long and thin to
    be a marker, and ValueError if it cannot be rendered.

    Both output dimensions are passed to cairosvg: given only a width, it
    derives the height from the SVG itself, so a tall SVG could allocate a
    raster of any height before anything else gets to validate it.
    """
    output_width, output_height = svg_raster_size(svg_bytes)
    try:
        return cairosvg.svg2png(
            bytestring=svg_bytes,
            output_width=output_width,
            output_height=output_height,
        )
    except Exception as e:
        raise ValueError(f"Could not render SVG: {e}") from e
