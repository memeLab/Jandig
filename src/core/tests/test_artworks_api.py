"""Test using the artwork API for Jandig Artwork"""

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from core.models import Artwork, Marker, Object
from core.tests.factory import ArtworkFactory
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
        )
        self.assertEqual(artwork.author, self.profile)

        response = self.client.get(f"/api/v1/artworks/{str(artwork.id)}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        assert data["id"] == artwork.id
        assert data["title"] == artwork.title
        assert data["description"] == artwork.description
        assert data["author"]["id"] == self.profile.id
        assert data["marker"]["id"] == marker.id
        assert data["augmented"]["id"] == obj.id

    def test_retrieve_artwork_as_modal(self):
        artwork = ArtworkFactory()
        response = self.client.get(f"/api/v1/artworks/{str(artwork.id)}/?format=modal")
        self.assertEqual(response.status_code, 200)
        html = response.content.decode("utf-8")

        assert artwork.title in html
        assert artwork.description in html
        assert artwork.marker.title in html
        assert artwork.marker.as_html(height=300, width=300) in html
        assert artwork.augmented.title in html
        assert artwork.augmented.as_html() in html
        assert artwork.author.user.username in html
        assert artwork.created_at.strftime("%d/%m/%Y") in html
