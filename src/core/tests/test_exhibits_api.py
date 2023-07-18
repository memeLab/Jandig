"""Test using the exhibit API for Jandig Exhibit"""

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from core.models import Artwork, Exhibit, Marker, Object
from users.models import User

fake_file = SimpleUploadedFile("fake_file.png", b"these are the file contents!")


class TestExhibitAPI(TestCase):
    def setUp(self):
        self.user = User.objects.create()
        self.profile = self.user.profile

    def test_url(self):
        response = self.client.get("/api/v1/exhibits/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 0)
        self.assertEqual(data["next"], None)
        self.assertEqual(data["previous"], None)
        self.assertEqual(data["results"], [])

    def test_api_exhibits_lists_one_exhibit(self):
        marker = Marker.objects.create(owner=self.profile, source=fake_file)
        obj = Object.objects.create(owner=self.profile, source=fake_file)
        artwork = Artwork.objects.create(
            author=self.profile, augmented=obj, marker=marker
        )
        exhibit = Exhibit.objects.create(owner=self.profile, name="test")
        exhibit.artworks.add(artwork)
        response = self.client.get("/api/v1/artworks/")
        self.assertEqual(response.status_code, 200)

    def test_api_exhibit_lists_multiple_exhibits(self):
        for i in range(0, settings.PAGE_SIZE + 1):
            response = self.client.get("/api/v1/exhibits/")
            self.assertEqual(response.status_code, 200)

    def test_retrieve_exhibit(self):
        marker = Marker.objects.create(owner=self.profile, source=fake_file)
        obj = Object.objects.create(owner=self.profile, source=fake_file)
        artwork = Artwork.objects.create(
            author=self.profile, augmented=obj, marker=marker
        )
        exhibit = Exhibit.objects.create(owner=self.profile, name="test")
        exhibit.artworks.add(artwork)
        response = self.client.get("/api/v1/exhibits/1/")
        self.assertEqual(response.status_code, 200)
