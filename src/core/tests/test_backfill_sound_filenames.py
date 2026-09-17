import re
from io import StringIO
from unittest import mock

from django.core.files.base import ContentFile
from django.core.management import call_command
from django.test import TestCase

from core.models import Sound, SoundExtensions
from users.tests.factory import ProfileFactory

GENERATED = re.compile(r"^sounds/[0-9a-f]{32}\.mp3$")


def legacy_sound(owner, filename="Música #1 (final).mp3"):
    """A row as it looks before #982: stored under the uploader's own name."""
    sound = Sound.objects.create(
        title=filename,
        author="A",
        owner=owner,
        file_extension=SoundExtensions.MP3,
        file_name_original="",
    )
    # Bypass upload_to so the old layout can be reproduced verbatim.
    sound.file.name = f"sounds/{filename}"
    sound.file.storage.save(sound.file.name, ContentFile(b"audio-bytes"))
    sound.save(update_fields=["file"])
    return sound


class TestBackfillSoundFilenames(TestCase):
    def setUp(self):
        self.owner = ProfileFactory()

    def run_command(self, **kwargs):
        out = StringIO()
        call_command("backfill_sound_filenames", stdout=out, stderr=out, **kwargs)
        return out.getvalue()

    def test_a_legacy_file_is_moved_to_a_generated_name(self):
        sound = legacy_sound(self.owner)

        self.run_command()
        sound.refresh_from_db()

        assert GENERATED.match(sound.file.name), sound.file.name
        assert "Música" not in sound.file.name

    def test_the_content_survives_the_move(self):
        sound = legacy_sound(self.owner)

        self.run_command()
        sound.refresh_from_db()

        with sound.file.open("rb") as handle:
            assert handle.read() == b"audio-bytes"

    def test_the_old_object_is_removed_from_storage(self):
        sound = legacy_sound(self.owner)
        old_name = sound.file.name

        self.run_command()

        assert not sound.file.storage.exists(old_name)

    def test_the_original_filename_is_preserved_when_it_was_empty(self):
        sound = legacy_sound(self.owner)

        self.run_command()
        sound.refresh_from_db()

        assert sound.file_name_original == "Música #1 (final).mp3"

    def test_an_already_generated_name_is_left_alone(self):
        sound = legacy_sound(self.owner)
        self.run_command()
        sound.refresh_from_db()
        settled = sound.file.name

        output = self.run_command()
        sound.refresh_from_db()

        assert sound.file.name == settled, "a second run must not rename again"
        assert "Nothing to do" in output

    def test_dry_run_changes_nothing(self):
        sound = legacy_sound(self.owner)
        before = sound.file.name

        output = self.run_command(dry_run=True)
        sound.refresh_from_db()

        assert sound.file.name == before
        assert "would rename" in output
        assert "Dry run" in output

    def test_limit_processes_only_the_first_rows(self):
        first = legacy_sound(self.owner, "one.mp3")
        second = legacy_sound(self.owner, "two.mp3")

        self.run_command(limit=1)
        first.refresh_from_db()
        second.refresh_from_db()

        assert GENERATED.match(first.file.name)
        assert second.file.name == "sounds/two.mp3"

    def test_one_failure_does_not_abort_the_batch(self):
        broken = legacy_sound(self.owner, "broken.mp3")
        healthy = legacy_sound(self.owner, "healthy.mp3")
        real_open = Sound.file.field.attr_class.open

        def fail_for_broken(self_file, *args, **kwargs):
            if "broken" in (self_file.name or ""):
                raise OSError("cannot read")
            return real_open(self_file, *args, **kwargs)

        with mock.patch.object(Sound.file.field.attr_class, "open", fail_for_broken):
            output = self.run_command()

        broken.refresh_from_db()
        healthy.refresh_from_db()

        assert broken.file.name == "sounds/broken.mp3", "the failure stays untouched"
        assert GENERATED.match(healthy.file.name), "the rest of the batch proceeds"
        assert "failed" in output
        assert "re-run to retry" in output
