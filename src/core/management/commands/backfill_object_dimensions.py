"""Backfill `width`/`height` for `Object` rows (#690 phase 1)."""

import logging

from django.core.management.base import BaseCommand
from PIL import Image, UnidentifiedImageError

from core.models import Object

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Populate Object.width/height for raster uploads that don't have them yet (#690 phase 1)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Probe files but don't save changes.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        # Phase 1 only handles GIF; mp4/webm/glb need ffprobe / GLTF
        # parsing and are out of scope until the wider plan lands.
        queryset = Object.objects.filter(
            file_extension="gif",
            width__isnull=True,
        )
        total = queryset.count()
        self.stdout.write(f"Probing {total} GIF Object rows missing dimensions.")

        updated = 0
        skipped = 0
        for obj in queryset.iterator(chunk_size=200):
            try:
                obj.source.open("rb")
                with Image.open(obj.source) as image:
                    width, height = image.size
            except (UnidentifiedImageError, OSError, FileNotFoundError) as exc:
                log.warning("Could not probe Object %s: %s", obj.pk, exc)
                skipped += 1
                continue
            finally:
                try:
                    obj.source.close()
                except Exception:
                    pass

            if dry_run:
                self.stdout.write(f"  [dry-run] Object {obj.pk}: {width}x{height}")
            else:
                obj.width = width
                obj.height = height
                obj.save(update_fields=["width", "height"])
            updated += 1

        action = "would update" if dry_run else "updated"
        self.stdout.write(
            self.style.SUCCESS(
                f"{action} {updated}/{total} rows ({skipped} skipped due to read errors)."
            )
        )
