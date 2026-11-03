"""Move sound files stored under their uploader's filename to generated names.

See #991. New uploads already land at `sounds/<uuid>.<ext>` (#982); this walks
the rows that predate that and brings them into line.
"""

import logging
import re

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from core.models import Sound, sound_file_path

log = logging.getLogger(__name__)

# What `sound_file_path` produces: sounds/<32 hex chars>[.ext]
GENERATED_NAME = re.compile(r"^sounds/[0-9a-f]{32}(\.[A-Za-z0-9]+)?$")


class Command(BaseCommand):
    help = (
        "Rename existing Sound files from the uploader's filename to a "
        "generated one. Safe to re-run: rows already renamed are skipped, so "
        "an interrupted run resumes by running it again."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would change without touching storage or the database.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Process at most this many rows, so a first batch can be small.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        limit = options["limit"]

        pending = [
            sound
            for sound in Sound.objects.exclude(file="").order_by("pk")
            if not GENERATED_NAME.match(sound.file.name or "")
        ]
        if limit is not None:
            pending = pending[:limit]

        if not pending:
            self.stdout.write(
                self.style.SUCCESS(
                    "Nothing to do: every sound file already has a generated name."
                )
            )
            return

        self.stdout.write(
            f"{len(pending)} sound file(s) still stored under a user-supplied name."
        )

        renamed = failed = 0
        for sound in pending:
            old_name = sound.file.name
            try:
                if dry_run:
                    self.stdout.write(
                        f"  would rename {old_name} "
                        f"-> {sound_file_path(sound, old_name)}"
                    )
                    continue
                new_name = self._rename(sound, old_name)
            except Exception:
                # One unreadable or unwritable object must not abort the run:
                # the whole point of a command over a migration is that the
                # rest of the batch still gets done, and the key is recorded.
                failed += 1
                log.exception("Could not rename sound %s (%s)", sound.pk, old_name)
                self.stderr.write(
                    self.style.ERROR(f"  failed: {old_name} (sound {sound.pk})")
                )
                continue
            renamed += 1
            self.stdout.write(f"  {old_name} -> {new_name}")

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run: nothing was changed."))
            return

        self.stdout.write(self.style.SUCCESS(f"Renamed {renamed} file(s)."))
        if failed:
            self.stdout.write(
                self.style.ERROR(
                    f"{failed} file(s) failed and were left as they were; "
                    "re-run to retry them."
                )
            )

    @staticmethod
    def _rename(sound, old_name):
        """Write the new object, point the row at it, then drop the old one.

        The order matters. Interrupted between any two steps, the worst
        outcome is an orphaned old object, never a row pointing at a key that
        no longer exists.
        """
        storage = sound.file.storage
        with sound.file.open("rb") as handle:
            content = handle.read()

        if not sound.file_name_original:
            sound.file_name_original = old_name.rsplit("/", 1)[-1]

        # FileField.save writes through storage and resets the cached handle.
        sound.file.save(
            sound_file_path(sound, old_name), ContentFile(content), save=True
        )
        new_name = sound.file.name

        if old_name != new_name and storage.exists(old_name):
            storage.delete(old_name)
        return new_name
