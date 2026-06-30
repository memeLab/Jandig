from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image
from pymarker import generate_marker_from_image, generate_patt_from_image

BLACK_BORDER_PERCENTAGE = 20
WHITE_BORDER_PERCENTAGE = 3
INNER_BORDER_PERCENTAGE = 2

MARKER_SIZE = (256, 256)
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

    # 5. Generate patt from original image (no borders)
    patt_str = generate_patt_from_image(original_image)
    patt_path = f"markers/{marker.pk}/marker.patt"
    _save_to_storage(storage, patt_path, patt_str.encode("utf-8"))
    marker.patt.name = patt_path

    # 6. Update file_size (size of print image for download reference)
    marker.file_size = len(print_blob.getvalue())

    # Save updated fields
    marker.save(
        update_fields=[
            "source",
            "marker_img",
            "print_img",
            "thumb_img",
            "patt",
            "file_size",
        ]
    )

    # Clean up the old source file if it moved to a new path
    if old_source_name and old_source_name != marker.source.name:
        try:
            if storage.exists(old_source_name):
                storage.delete(old_source_name)
        except Exception:
            pass  # Non-critical cleanup


def delete_marker_files(marker):
    """Delete all image files and the folder for a marker."""
    fields = [
        marker.source,
        marker.marker_img,
        marker.print_img,
        marker.thumb_img,
        marker.patt,
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
