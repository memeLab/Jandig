"""
Data migration: relocate all existing Object files to the new
per-object-ID folder structure: objects/<pk>/source.<ext>, etc.
"""

import logging

from django.core.files.base import ContentFile
from django.db import migrations

logger = logging.getLogger(__name__)


def relocate_object_files(apps, schema_editor):
    """Move all Object files from flat folders to objects/<pk>/ structure."""
    Object = apps.get_model("core", "Object")

    for obj in Object.objects.all().iterator():
        if not obj.source:
            logger.warning("Object %s: no source file, skipping.", obj.pk)
            continue

        storage = obj.source.storage
        changed = False

        def _move(current_name, target_path):
            nonlocal changed
            if not current_name:
                return current_name
            if current_name == target_path:
                return current_name
            try:
                if not storage.exists(current_name):
                    logger.warning(
                        "Object %s: file %s not found, skipping.",
                        obj.pk,
                        current_name,
                    )
                    return current_name
                content = storage.open(current_name).read()
                # Delete target if it already exists
                try:
                    if storage.exists(target_path):
                        storage.delete(target_path)
                except Exception:
                    pass
                storage.save(target_path, ContentFile(content))
                # Delete old file
                try:
                    storage.delete(current_name)
                except Exception:
                    pass
                changed = True
                return target_path
            except Exception as e:
                logger.error(
                    "Object %s: failed to move %s -> %s: %s",
                    obj.pk,
                    current_name,
                    target_path,
                    e,
                )
                return current_name

        # Source file
        ext = (
            obj.source.name.rsplit(".", 1)[-1].lower()
            if "." in obj.source.name
            else ""
        )
        obj.source.name = _move(obj.source.name, f"objects/{obj.pk}/source.{ext}")

        # Audio description
        if obj.audio_description:
            ad_ext = (
                obj.audio_description.name.rsplit(".", 1)[-1].lower()
                if "." in obj.audio_description.name
                else ""
            )
            obj.audio_description.name = _move(
                obj.audio_description.name,
                f"objects/{obj.pk}/audio_description.{ad_ext}",
            )

        # Thumbnail
        if obj.thumbnail:
            obj.thumbnail.name = _move(
                obj.thumbnail.name, f"objects/{obj.pk}/thumbnail.png"
            )

        # Spritesheet
        if obj.spritesheet_file:
            obj.spritesheet_file.name = _move(
                obj.spritesheet_file.name, f"objects/{obj.pk}/spritesheet.png"
            )

        # Spritesheet metadata
        if obj.spritesheet_metadata:
            obj.spritesheet_metadata.name = _move(
                obj.spritesheet_metadata.name, f"objects/{obj.pk}/metadata.json"
            )

        if changed:
            obj.save()
            logger.info("Object %s: files relocated successfully.", obj.pk)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0030_object_spritesheet_fields"),
    ]

    operations = [
        migrations.RunPython(
            relocate_object_files,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
