"""Test using the artwork API for Jandig Artwork"""

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from core.models import Artwork, Marker, Object
from users.models import User

fake_file = SimpleUploadedFile("fake_file.png", b"these are the file contents!")


class TestArtworkAPI(TestCase):
    def setUp(self):
        self.user = User.objects.create()
        self.profile = self.user.profile

    def test_url(self):
        response = self.client.get("/api/v1/artworks/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 0)
        self.assertEqual(data["next"], None)
        self.assertEqual(data["previous"], None)
        self.assertEqual(data["results"], [])

    def test_api_artworks_lists_one_artwork(self):
        marker = Marker.objects.create(owner=self.profile, source=fake_file)
        obj = Object.objects.create(owner=self.profile, source=fake_file)
        artwork = Artwork.objects.create(
            author=self.profile, augmented=obj, marker=marker
        )
        self.assertEqual(artwork.author, self.profile)
        response = self.client.get("/api/v1/artworks/")
        self.assertEqual(response.status_code, 200)

    def test_api_artwork_lists_multiple_artworks(self):
        for _ in range(0, settings.PAGE_SIZE + 1):
            marker = Marker.objects.create(owner=self.profile, source=fake_file)
            obj = Object.objects.create(owner=self.profile, source=fake_file)
            Artwork.objects.create(author=self.profile, augmented=obj, marker=marker)

        response = self.client.get("/api/v1/artworks/")
        self.assertEqual(response.status_code, 200)

    def test_retrieve_artwork(self):
        marker = Marker.objects.create(owner=self.profile, source=fake_file)
        obj = Object.objects.create(owner=self.profile, source=fake_file)
        artwork = Artwork.objects.create(
            author=self.profile, augmented=obj, marker=marker
        )  # noqa F841
        self.assertEqual(artwork.author, self.profile)

        response = self.client.get("/api/v1/artworks/1/")
        self.assertEqual(response.status_code, 200)
