import re
from unittest import mock

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.test import TestCase
from django.urls import reverse

from core.models import Sound, SoundExtensions
from core.sound_filenames import (
    rename_to_generated_name,
    with_generated_name,
    with_legacy_name,
)
from users.tests.factory import ProfileFactory

GENERATED = re.compile(r"^sounds/[0-9a-f]{32}\.mp3$")
ACTION = "rename_files_to_generated_names"


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


def uploaded_sound(owner):
    """A row as #982 stores it: under a generated name."""
    return Sound.objects.create(
        title="new",
        author="A",
        owner=owner,
        file_extension=SoundExtensions.MP3,
        file_name_original="new.mp3",
        file=ContentFile(b"audio-bytes", name="new.mp3"),
    )


class TestRenameToGeneratedName(TestCase):
    def setUp(self):
        self.owner = ProfileFactory()

    def test_a_legacy_file_is_moved_to_a_generated_name(self):
        sound = legacy_sound(self.owner)

        new_name = rename_to_generated_name(sound)
        sound.refresh_from_db()

        assert sound.file.name == new_name
        assert GENERATED.match(sound.file.name), sound.file.name
        assert "Música" not in sound.file.name

    def test_the_content_survives_the_move(self):
        sound = legacy_sound(self.owner)

        rename_to_generated_name(sound)
        sound.refresh_from_db()

        with sound.file.open("rb") as handle:
            assert handle.read() == b"audio-bytes"

    def test_the_old_object_is_removed_from_storage(self):
        sound = legacy_sound(self.owner)
        old_name = sound.file.name

        rename_to_generated_name(sound)

        assert not sound.file.storage.exists(old_name)

    def test_the_original_filename_is_preserved_when_it_was_empty(self):
        sound = legacy_sound(self.owner)

        rename_to_generated_name(sound)
        sound.refresh_from_db()

        assert sound.file_name_original == "Música #1 (final).mp3"

    def test_a_recorded_original_filename_is_kept(self):
        sound = legacy_sound(self.owner)
        sound.file_name_original = "what the user called it.mp3"
        sound.save(update_fields=["file_name_original"])

        rename_to_generated_name(sound)
        sound.refresh_from_db()

        assert sound.file_name_original == "what the user called it.mp3"


class TestLegacyNameQuerysets(TestCase):
    def setUp(self):
        self.owner = ProfileFactory()

    def test_a_new_upload_counts_as_generated(self):
        sound = uploaded_sound(self.owner)

        assert GENERATED.match(sound.file.name), sound.file.name
        assert list(with_generated_name(Sound.objects.all())) == [sound]
        assert not with_legacy_name(Sound.objects.all()).exists()

    def test_a_user_supplied_name_counts_as_legacy(self):
        sound = legacy_sound(self.owner)

        assert list(with_legacy_name(Sound.objects.all())) == [sound]
        assert not with_generated_name(Sound.objects.all()).exists()

    def test_a_name_that_only_resembles_a_generated_one_is_legacy(self):
        lookalikes = [
            legacy_sound(self.owner, "0123456789abcdef.mp3"),
            legacy_sound(self.owner, f"{'a' * 32} copy.mp3"),
            legacy_sound(self.owner, f"{'A' * 32}.mp3"),
        ]

        assert set(with_legacy_name(Sound.objects.all())) == set(lookalikes)

    def test_a_sound_without_a_file_is_in_neither(self):
        Sound.objects.create(
            title="empty",
            author="A",
            owner=self.owner,
            file_extension=SoundExtensions.MP3,
        )

        assert not with_legacy_name(Sound.objects.all()).exists()
        assert not with_generated_name(Sound.objects.all()).exists()


class TestSoundAdminRename(TestCase):
    """The backfill runs from the admin: the deployments have no console."""

    def setUp(self):
        self.owner = ProfileFactory()
        admin = User.objects.create_superuser("admin", "admin@example.com", "pw")
        self.client.force_login(admin)
        self.changelist = reverse("admin:core_sound_changelist")

    def run_action(self, *sounds):
        # Following the redirect renders the list, which is what consumes the
        # messages: without it they pile up across calls.
        response = self.client.post(
            self.changelist,
            {"action": ACTION, "_selected_action": [sound.pk for sound in sounds]},
            follow=True,
        )
        assert response.redirect_chain, "the action should redirect to the list"
        return [str(message) for message in response.context["messages"]]

    def test_the_action_is_offered_on_the_sound_list(self):
        legacy_sound(self.owner)

        content = self.client.get(self.changelist).content.decode()

        assert f'value="{ACTION}"' in content

    def test_selected_legacy_sounds_are_renamed(self):
        first = legacy_sound(self.owner, "one.mp3")
        second = legacy_sound(self.owner, "two.mp3")

        messages = self.run_action(first, second)
        first.refresh_from_db()
        second.refresh_from_db()

        assert GENERATED.match(first.file.name)
        assert GENERATED.match(second.file.name)
        assert messages == ["Renamed 2 sound file(s)."]

    def test_sounds_that_were_not_selected_are_left_alone(self):
        chosen = legacy_sound(self.owner, "one.mp3")
        other = legacy_sound(self.owner, "two.mp3")

        self.run_action(chosen)
        other.refresh_from_db()

        assert other.file.name == "sounds/two.mp3"

    def test_running_it_again_does_not_rename_again(self):
        sound = legacy_sound(self.owner)
        self.run_action(sound)
        sound.refresh_from_db()
        settled = sound.file.name

        messages = self.run_action(sound)
        sound.refresh_from_db()

        assert sound.file.name == settled
        assert messages == ["Renamed 0 sound file(s). 1 needed no rename."]

    def test_one_failure_does_not_stop_the_others(self):
        broken = legacy_sound(self.owner, "broken.mp3")
        healthy = legacy_sound(self.owner, "healthy.mp3")
        real_open = Sound.file.field.attr_class.open

        def fail_for_broken(self_file, *args, **kwargs):
            if "broken" in (self_file.name or ""):
                raise OSError("cannot read")
            return real_open(self_file, *args, **kwargs)

        with mock.patch.object(Sound.file.field.attr_class, "open", fail_for_broken):
            messages = self.run_action(broken, healthy)

        broken.refresh_from_db()
        healthy.refresh_from_db()

        assert broken.file.name == "sounds/broken.mp3", "the failure stays untouched"
        assert GENERATED.match(healthy.file.name), "the rest proceeds"
        failure = (
            f"Could not rename sounds/broken.mp3 (sound {broken.pk}). "
            "It was left as it was."
        )
        assert messages == [failure, "Renamed 1 sound file(s)."]

    def test_a_file_missing_from_storage_is_reported_not_raised(self):
        sound = legacy_sound(self.owner, "gone.mp3")
        sound.file.storage.delete(sound.file.name)

        messages = self.run_action(sound)
        sound.refresh_from_db()

        assert sound.file.name == "sounds/gone.mp3"
        assert messages[0].startswith("Could not rename sounds/gone.mp3")

    def test_the_filter_lists_only_the_sounds_left_to_rename(self):
        legacy = legacy_sound(self.owner, "old.mp3")
        current = uploaded_sound(self.owner)

        def listed(value):
            response = self.client.get(self.changelist, {"file_name": value})
            return list(response.context["cl"].queryset)

        assert listed("legacy") == [legacy]
        assert listed("generated") == [current]

    def test_the_action_needs_an_admin_login(self):
        sound = legacy_sound(self.owner)
        self.client.logout()

        self.client.post(
            self.changelist, {"action": ACTION, "_selected_action": [sound.pk]}
        )
        sound.refresh_from_db()

        assert sound.file.name == "sounds/Música #1 (final).mp3"
