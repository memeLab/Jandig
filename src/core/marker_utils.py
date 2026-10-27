import logging
import math
import time
from io import BytesIO
from types import SimpleNamespace

import cairosvg.surface
from cairosvg.helpers import node_format
from cairosvg.parser import Tree
from cairosvg.url import parse_url, safe_fetch
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
# The most pixels rendering one SVG may decode or allocate on top of the raster
# itself, checked separately for: all the images it embeds put together, each
# mask or pattern layer, and the group layers open at any one time. It is the
# size of the largest raster marker (MAX_MARKER_DIMENSION in forms.py, #980);
# at 4 bytes a pixel, 64 MiB.
MAX_SVG_LAYER_PIXELS = 4096 * 4096
# Rendering is abandoned past this. <use> and pattern references let a small
# SVG redraw the same content many thousands of times.
MAX_SVG_RENDER_SECONDS = 10
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


class SvgTooComplexError(ValueError):
    """Rendering the SVG would take more memory or time than a marker may use."""


# cairosvg decompresses an SVG that starts with gzip's magic number, whether
# uploaded or fetched from a data: URL inside one, in a single call with no
# size limit, so a few kilobytes can expand into gigabytes.
GZIP_MAGIC = b"\x1f\x8b"
# The raster formats an SVG may embed. cairosvg hands any other <image> to
# Pillow, which opens many more formats, some through external programs (EPS
# runs Ghostscript).
SVG_EMBEDDED_IMAGE_FORMATS = {"PNG", "JPEG", "MPO", "GIF", "WEBP"}


class _SvgRenderGuard:
    """
    Limits on the memory and time rendering one SVG may take beyond its
    raster, which SVG_RASTER_WIDTH already bounds. cairosvg also decodes
    every embedded image at its full size however small it is drawn,
    rasterises each mask and pattern at the size the SVG declares for it, and
    allocates a scratch layer the size of the surface for every group with
    opacity, a mask or a filter, nested as deeply as the SVG, or a chain of
    <use> references, nests them.
    """

    def __init__(self):
        self.embedded_pixels = 0
        self.layer_pixels = 0
        self.deadline = time.monotonic() + MAX_SVG_RENDER_SECONDS

    def fetch(self, url, resource_type):
        """
        A cairosvg url_fetcher: its default one, which only reads data: URLs,
        plus checks on what those URLs hold.
        """
        data = safe_fetch(url, resource_type)
        if data.startswith(GZIP_MAGIC):
            raise SvgTooComplexError("SVG embeds compressed content")
        if resource_type == "image/*" and not _is_drawn_as_svg(data):
            self._count_embedded_image(data)
        return data

    def _count_embedded_image(self, data):
        # Pillow reads only the header here, the same one cairo (for PNGs) or
        # Pillow (for the rest) sizes the decoded image from.
        try:
            with Image.open(BytesIO(data)) as image:
                image_format, (width, height) = image.format, image.size
        except Image.DecompressionBombError as e:
            raise SvgTooComplexError(f"SVG embeds a huge image: {e}") from e
        except Exception as e:
            raise ValueError(f"SVG embeds an unreadable image: {e}") from e
        if image_format not in SVG_EMBEDDED_IMAGE_FORMATS:
            raise ValueError(f"SVG embeds an unsupported {image_format} image")
        self.embedded_pixels += width * height
        if self.embedded_pixels > MAX_SVG_LAYER_PIXELS:
            raise SvgTooComplexError(
                f"SVG embeds images of {self.embedded_pixels} pixels in total"
            )

    def check_time(self):
        if time.monotonic() > self.deadline:
            raise SvgTooComplexError(
                f"SVG took more than {MAX_SVG_RENDER_SECONDS}s to render"
            )


def _is_drawn_as_svg(data):
    """Whether cairosvg's image() draws these <image> bytes as a nested SVG
    (or skips them, under 5 bytes) rather than decoding them as a raster."""
    if len(data) < 5:
        return True
    if data.startswith(b"\x89PNG"):
        return False
    return data.startswith((b"<svg ", b"<?xml", b"<!DOC", GZIP_MAGIC)) or (
        b"<svg" in data
    )


def _pushes_group(node):
    """Whether cairosvg's Surface.draw pushes a group for the node: a scratch
    layer as large as the surface, alive until the node and its children are
    drawn."""
    try:
        opacity = float(node.get("opacity", 1))
    except ValueError:
        # Surface.draw raises on its own when it gets there.
        opacity = 1
    return bool(
        parse_url(node.get("mask")).fragment
        or parse_url(node.get("filter")).fragment
        or (opacity < 1 and node.children)
    )


class _GuardedSurfaceMixin:
    """Applies a _SvgRenderGuard to a cairosvg surface. Without one, the
    surface behaves exactly like cairosvg's own."""

    guard = None

    def draw(self, node):
        guard = self.guard
        if guard is None:
            return super().draw(node)
        guard.check_time()
        layer_pixels = self.width * self.height if _pushes_group(node) else 0
        guard.layer_pixels += layer_pixels
        try:
            if guard.layer_pixels > MAX_SVG_LAYER_PIXELS:
                raise SvgTooComplexError(
                    "SVG nests too many groups with opacity, masks or filters"
                )
            super().draw(node)
        finally:
            guard.layer_pixels -= layer_pixels


class _GuardedPNGSurface(_GuardedSurfaceMixin, cairosvg.surface.PNGSurface):
    def __init__(self, guard, *args, **kwargs):
        self.guard = guard
        super().__init__(*args, **kwargs)


class _GuardedSVGSurface(_GuardedSurfaceMixin, cairosvg.surface.SVGSurface):
    """cairosvg's SVGSurface, which it also draws masks and patterns on, taking
    the guard of the surface it draws them for."""

    def __init__(self, tree, output, dpi, parent_surface=None, *args, **kwargs):
        self.guard = getattr(parent_surface, "guard", None)
        super().__init__(tree, output, dpi, parent_surface, *args, **kwargs)

    def _create_surface(self, width, height):
        # cairo records on this surface, but rasterises all of it, at this
        # size, whenever it is used as a mask or pattern on the raster.
        # Written so that NaN fails too.
        if self.guard is not None and not width * height <= MAX_SVG_LAYER_PIXELS:
            raise SvgTooComplexError(f"SVG needs a {width:g}x{height:g} layer")
        return super()._create_surface(width, height)


# cairosvg creates mask and pattern layers with `surface.SVGSurface(...)`,
# looked up each time one is drawn, so this is the one place they can be
# bounded. Only a guarded surface hands a guard on, so anything else that uses
# cairosvg behaves as before.
cairosvg.surface.SVGSurface = _GuardedSVGSurface


def svg_intrinsic_size(svg_bytes):
    """
    Return the (width, height) cairosvg would give the SVG, in px, without
    rendering it: the root's width and height, each falling back to the
    viewBox when missing or relative. Raises ValueError if the SVG cannot be
    parsed or has no usable size.
    """
    if svg_bytes.startswith(GZIP_MAGIC):
        raise ValueError("Could not render SVG: compressed SVGs are not supported")
    try:
        # Parsing already fetches the data: URL of any <tref>.
        tree = Tree(bytestring=svg_bytes, url_fetcher=_SvgRenderGuard().fetch)
        # Mirrors the state cairosvg's own surface is in when it sizes the
        # root: 96 dpi, 12pt font, and no parent to resolve percentages against.
        surface = SimpleNamespace(
            context_width=None, context_height=None, dpi=96, font_size=16
        )
        width, height, _viewbox = node_format(surface, tree)
    except SvgTooComplexError:
        raise
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
    be a marker, SvgTooComplexError if its content would take more than
    MAX_SVG_LAYER_PIXELS or MAX_SVG_RENDER_SECONDS to render, and ValueError
    if it cannot be rendered.

    Both output dimensions are passed to cairosvg: given only a width, it
    derives the height from the SVG itself, so a tall SVG could allocate a
    raster of any height before anything else gets to validate it.
    """
    output_width, output_height = svg_raster_size(svg_bytes)
    guard = _SvgRenderGuard()
    output = BytesIO()
    try:
        # What cairosvg.svg2png does, with the guard attached.
        tree = Tree(bytestring=svg_bytes, url_fetcher=guard.fetch)
        _GuardedPNGSurface(
            guard,
            tree,
            output,
            96,
            output_width=output_width,
            output_height=output_height,
        ).finish()
    except SvgTooComplexError:
        raise
    except Exception as e:
        raise ValueError(f"Could not render SVG: {e}") from e
    return output.getvalue()
