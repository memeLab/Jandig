"""Test using the sound API for Jandig Sounds"""

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from core.models import Sound
from core.serializers import SoundSerializer
from users.models import User

fake_file = SimpleUploadedFile("fake_file.png", b"these are the file contents!")


class TestSoundAPI(TestCase):
    def setUp(self):
        self.user = User.objects.create()
        self.profile = self.user.profile

    def test_url(self):
        response = self.client.get("/api/v1/sounds/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 0)
        self.assertEqual(data["next"], None)
        self.assertEqual(data["previous"], None)
        self.assertEqual(data["results"], [])

    def test_api_sounds_lists_one_sound(self):
        # Create an object
        sound = Sound.objects.create(owner=self.profile, file=fake_file)

        response = self.client.get("/api/v1/sounds/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["next"], None)
        self.assertEqual(data["previous"], None)
        first_result = data["results"][0]
        serializer_data = SoundSerializer(sound).data
        # Asserts the serializer is being used by the endpoint
        assert first_result == serializer_data

        # Asserts the serializer uses all the needed fields
        self.assertIn("id", first_result)
        self.assertIn("owner", first_result)
        self.assertIn("file", first_result)
        self.assertIn("created", first_result)
        self.assertIn("author", first_result)
        self.assertIn("title", first_result)

    def test_api_sounds_lists_multiple_sounds(self):
        for _ in range(0, settings.PAGE_SIZE + 1):
            Sound.objects.create(owner=self.profile, file=fake_file)

        response = self.client.get("/api/v1/sounds/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], settings.PAGE_SIZE + 1)
        self.assertEqual(
            data["next"],
            f"http://testserver/api/v1/sounds/?limit={settings.PAGE_SIZE}&offset={settings.PAGE_SIZE}",
        )
        self.assertEqual(data["previous"], None)
        self.assertEqual(len(data["results"]), 20)

    def test_retrieve_sound(self):
        # Create a sound
        sound = Sound.objects.create(owner=self.profile, file=fake_file)

        response = self.client.get(f"/api/v1/sounds/{sound.id}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        serializer_data = SoundSerializer(sound).data
        # Asserts the serializer is being used by the endpoint
        assert data == serializer_data

    def test_retrieve_sound_as_modal(self):
        # Create a sound
        sound = Sound.objects.create(owner=self.profile, file=fake_file)

        response = self.client.get(f"/api/v1/sounds/{sound.id}/?format=modal")
        self.assertEqual(response.status_code, 200)
        html = response.content.decode("utf-8")
        assert sound.title in html
        assert sound.created.strftime("%d/%m/%Y") in html
        assert sound.author in html
        assert sound.owner.user.username in html
        assert str(sound.file_size) in html
        assert sound.used_in_html_string() in html
        assert "<audio" in html
