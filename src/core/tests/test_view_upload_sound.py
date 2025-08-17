from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from core.models import Sound, SoundExtensions
from users.models import Profile, User

EXAMPLE_SOUND_PATH = "collection/sounds/happy-message-ping.mp3"
EXAMPLE_SOUND_FILE_SIZE = 36096  # Size in bytes of the example sound file


class TestSoundUpload(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "testpassword"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            is_staff=False,
            is_superuser=False,
        )
        self.profile = Profile.objects.get(user=self.user)

    def test_upload_sound_unauthenticated(self):
        url = reverse("sound-upload")
        with open(EXAMPLE_SOUND_PATH, "rb") as image_file:
            data = {
                "file": image_file,
                "author": "Test Author",
                "title": "Test Marker",
            }
            response = self.client.post(url, data)
        assert response.status_code == status.HTTP_302_FOUND  # Redirect to login page
        assert "/users/login" in response.url
        assert Sound.objects.count() == 0

    def test_upload_sound_authenticated(self):
        with open(EXAMPLE_SOUND_PATH, "rb") as sound_file:
            data = {
                "file": sound_file,
                "author": "Test Author",
                "title": "Test Marker",
            }

            self.client.login(username=self.username, password=self.password)
            response = self.client.post(reverse("sound-upload"), data)
            assert (
                response.status_code == status.HTTP_302_FOUND
            )  # Redirect to home page

        # Verify that a Sound instance was created
        assert Sound.objects.count() == 1
        sound = Sound.objects.first()
        assert sound.title == "Test Marker"
        assert sound.author == "Test Author"
        assert sound.file_size == EXAMPLE_SOUND_FILE_SIZE

        assert sound.file_name_original == "happy-message-ping.mp3"
        assert sound.file_extension == SoundExtensions.MP3

    def test_upload_sound_get_authenticated(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse("sound-upload"))
        assert response.status_code == 200
        assert b"Sound's title" in response.content  # Form is rendered

    def test_upload_sound_post_invalid_missing_fields(self):
        self.client.login(username=self.username, password=self.password)
        data = {
            "author": "Test Author",
            "title": "Test Marker",
            # Missing 'file'
        }
        response = self.client.post(reverse("sound-upload"), data)
        assert response.status_code == 200
        assert b"This field is required" in response.content
        assert Sound.objects.count() == 0

        data = {
            "file": SimpleUploadedFile("test.gif", b"test content"),
            # missing 'title'
            "author": "Test Author",
        }

        response = self.client.post(reverse("sound-upload"), data)
        assert response.status_code == 200
        assert b"This field is required" in response.content
        assert Sound.objects.count() == 0

    def test_upload_sound_post_invalid_file_type(self):
        self.client.login(username=self.username, password=self.password)
        fake_file = SimpleUploadedFile(
            "test.txt", b"not an image", content_type="text/plain"
        )
        data = {
            "file": fake_file,
            "author": "Test Author",
            "title": "Test Marker",
        }
        response = self.client.post(reverse("sound-upload"), data)
        # Should fail validation or be rejected by the form
        assert response.status_code == 200
        assert b"Only MP3, OGG, and WAV audio files are allowed." in response.content
        assert Sound.objects.count() == 0

    def test_upload_sound_permission_denied_for_anonymous(self):
        response = self.client.get(reverse("sound-upload"))
        assert response.status_code == status.HTTP_302_FOUND
        assert "/users/login" in response.url
