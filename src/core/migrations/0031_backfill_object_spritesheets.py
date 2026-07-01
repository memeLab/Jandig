"""
Data migration: generate spritesheets and metadata JSON files for all
existing GIF Objects that don't have them yet.
"""

import json
import logging

from django.core.files.base import ContentFile
from django.db import migrations
from src.core.spritesheet_converter import gif_to_spritesheet

logger = logging.getLogger(__name__)


def generate_spritesheets_for_existing_gifs(apps, schema_editor):
    # Import inline so that the migration doesn't break if the module is
    # moved or renamed later — the function body is self-contained.
    

    Object = apps.get_model("core", "Object")

    for obj in Object.objects.filter(file_extension="gif").iterator():
        if not obj.source:
            logger.warning("Object %s: no source file, skipping.", obj.pk)
            continue

        try:
            storage = obj.source.storage

            with obj.source.open("rb") as f:
                png_bytes, metadata = gif_to_spritesheet(f)

            base_name = obj.source.name.rsplit(".", 1)[0].split("/")[-1]

            # Save spritesheet PNG
            spritesheet_path = f"objects/spritesheets/{base_name}_spritesheet.png"
            _save_to_storage(storage, spritesheet_path, png_bytes)
            obj.spritesheet_file.name = spritesheet_path

            # Save metadata JSON
            metadata_path = f"objects/spritesheets/{base_name}_spritesheet.json"
            _save_to_storage(
                storage, metadata_path, json.dumps(metadata).encode("utf-8")
            )
            obj.spritesheet_metadata.name = metadata_path

            obj.save()
            logger.info("Object %s (%s): spritesheet generated.", obj.pk, base_name)

        except Exception as e:
            logger.error(
                "Object %s: failed to generate spritesheet: %s", obj.pk, e
            )
            continue


def _save_to_storage(storage, path, content_bytes):
    """Save content to storage, deleting existing file first for idempotency."""
    try:
        if storage.exists(path):
            storage.delete(path)
    except Exception:
        pass
    storage.save(path, ContentFile(content_bytes))


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0030_object_spritesheet_fields"),
    ]

    operations = [
        migrations.RunPython(
            generate_spritesheets_for_existing_gifs,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
