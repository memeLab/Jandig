"""
Data migration: fix Object file paths in the database.

Migration 0031 moved files to objects/<pk>/ folders but failed to persist
the new paths in the DB.
This migration updates the DB to match the actual file locations.
"""

import logging

from django.db import migrations

logger = logging.getLogger(__name__)


def fix_object_file_paths(apps, schema_editor):
    """Update DB paths to match the objects/<pk>/ folder structure."""
    Object = apps.get_model("core", "Object")

    for obj in Object.objects.only(
        "pk", "source", "audio_description", "thumbnail",
        "spritesheet_file", "spritesheet_metadata",
    ).iterator():
        if not obj.source:
            continue

        storage = obj.source.storage
        updates = {}

        # Source file
        ext = (
            obj.source.name.rsplit(".", 1)[-1].lower()
            if "." in obj.source.name
            else ""
        )
        expected_source = f"objects/{obj.pk}/source.{ext}"
        if obj.source.name != expected_source:
            if storage.exists(expected_source):
                updates["source"] = expected_source

        # Audio description
        if obj.audio_description:
            ad_ext = (
                obj.audio_description.name.rsplit(".", 1)[-1].lower()
                if "." in obj.audio_description.name
                else ""
            )
            expected_ad = f"objects/{obj.pk}/audio_description.{ad_ext}"
            if obj.audio_description.name != expected_ad:
                if storage.exists(expected_ad):
                    updates["audio_description"] = expected_ad

        # Thumbnail
        if obj.thumbnail:
            expected_thumb = f"objects/{obj.pk}/thumbnail.png"
            if obj.thumbnail.name != expected_thumb:
                if storage.exists(expected_thumb):
                    updates["thumbnail"] = expected_thumb

        # Spritesheet
        if obj.spritesheet_file:
            expected_ss = f"objects/{obj.pk}/spritesheet.png"
            if obj.spritesheet_file.name != expected_ss:
                if storage.exists(expected_ss):
                    updates["spritesheet_file"] = expected_ss

        # Spritesheet metadata
        if obj.spritesheet_metadata:
            expected_meta = f"objects/{obj.pk}/metadata.json"
            if obj.spritesheet_metadata.name != expected_meta:
                if storage.exists(expected_meta):
                    updates["spritesheet_metadata"] = expected_meta

        if updates:
            Object.objects.filter(pk=obj.pk).update(**updates)
            logger.info("Object %s: paths fixed: %s", obj.pk, list(updates.keys()))


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0037_remove_object_insert_insert_and_more"),
    ]

    operations = [
        migrations.RunPython(
            fix_object_file_paths,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
