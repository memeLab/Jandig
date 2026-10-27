import re

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from core.models import Sound, sound_file_path
from users.models import User

EXAMPLE_SOUND_PATH = "collection/sounds/happy-message-ping.mp3"
STORED_NAME = re.compile(r"^sounds/[0-9a-f]{32}\.mp3$")


class TestSoundUploadPath(TestCase):
    """Sound filenames come from the user; they must not reach storage as-is."""

    def setUp(self):
        self.username = "testuser"
        self.password = "testpassword"
        User.objects.create_user(username=self.username, password=self.password)
        self.client.login(username=self.username, password=self.password)

    def upload(self, filename):
        with open(EXAMPLE_SOUND_PATH, "rb") as handle:
            payload = handle.read()
        return self.client.post(
            reverse("sound-upload"),
            {
                "file": SimpleUploadedFile(
                    filename, payload, content_type="audio/mpeg"
                ),
                "title": filename,
                "author": "Test Author",
            },
        )

    def test_hostile_filename_never_reaches_storage(self):
        self.upload("Música #1 (versão final?) 100%.mp3")
        sound = Sound.objects.get(title="Música #1 (versão final?) 100%.mp3")

        assert STORED_NAME.match(sound.file.name), sound.file.name

    def test_original_filename_is_still_recorded(self):
        self.upload("Música #1 (versão final?) 100%.mp3")
        sound = Sound.objects.get(title="Música #1 (versão final?) 100%.mp3")

        assert sound.file_name_original.endswith(".mp3")
        assert sound.file_extension == "mp3"

    def test_two_uploads_of_the_same_name_do_not_collide(self):
        self.upload("same-name.mp3")
        self.upload("same-name.mp3")
        names = {sound.file.name for sound in Sound.objects.all()}

        assert len(names) == Sound.objects.count()

    def test_path_helper_lowercases_and_keeps_the_extension(self):
        assert sound_file_path(None, "Whatever.MP3").endswith(".mp3")
        assert STORED_NAME.match(sound_file_path(None, "a b/c?.mp3"))

    def test_path_helper_tolerates_a_name_without_extension(self):
        generated = sound_file_path(None, "noextension")

        assert re.match(r"^sounds/[0-9a-f]{32}$", generated), generated
