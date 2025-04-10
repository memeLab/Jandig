"""Test using the exhibit API for Jandig Exhibit"""

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from core.models import Artwork, Exhibit, Marker, Object
from core.serializers import ArtworkSerializer
from core.tests.factory import ExhibitFactory
from users.models import User
from users.tests.factory import ProfileFactory

fake_file = SimpleUploadedFile("fake_file.png", b"these are the file contents!")


class TestExhibitAPI(TestCase):
    def setUp(self):
        self.user = User.objects.create()
        self.profile = self.user.profile

    def test_url(self):
        """Test that the root page of the api exists"""
        response = self.client.get("/api/v1/exhibits/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 0)
        self.assertEqual(data["next"], None)
        self.assertEqual(data["previous"], None)
        self.assertEqual(data["results"], [])

    def test_api_exhibits_lists_one_exhibit(self):
        """API returns one exhibit if there is one exhibit"""
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
        """API returns multiple exhibits if there are multiple exhibits"""
        for i in range(0, settings.PAGE_SIZE + 1):
            marker = Marker.objects.create(owner=self.profile, source=fake_file)
            obj = Object.objects.create(owner=self.profile, source=fake_file)
            Artwork.objects.create(author=self.profile, augmented=obj, marker=marker)
            Exhibit.objects.create(
                owner=self.profile, name=f"name_{i}", slug=f"slug_{i}"
            )
        response = self.client.get("/api/v1/exhibits/")
        self.assertEqual(response.status_code, 200)

    def test_retrieve_exhibit(self):
        """Test that the exhibit can be retrieved using its ID on the API path"""
        marker = Marker.objects.create(owner=self.profile, source=fake_file)
        obj = Object.objects.create(owner=self.profile, source=fake_file)
        artwork = Artwork.objects.create(
            author=self.profile, augmented=obj, marker=marker
        )
        exhibit = Exhibit.objects.create(owner=self.profile, name="test")
        exhibit.artworks.add(artwork)
        response = self.client.get(f"/api/v1/exhibits/{str(exhibit.id)}/")
        self.assertEqual(response.status_code, 200)

    def test_searching_exhibits(self):
        """Test that the exhibit can be searched using owner id"""
        user = ProfileFactory()
        exhibit = ExhibitFactory(owner=user)

        # Extra exhibit from another owner to check if it is not included
        _ = ExhibitFactory()

        response = self.client.get(f"/api/v1/exhibits/?owner={user.id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["id"] == exhibit.id
        assert data["results"][0]["name"] == exhibit.name
        assert data["results"][0]["slug"] == exhibit.slug
        assert data["results"][0]["owner"] == user.id
        assert (
            data["results"][0]["artworks"]
            == ArtworkSerializer(exhibit.artworks.all(), many=True).data
        )

    def test_searching_exhibits_by_invalid_owner(self):
        """Test that the exhibit cannot be searched using invalid owner id"""
        user = ProfileFactory()
        exhibit = ExhibitFactory(owner=user)

        # Extra exhibit from another owner to check if it is not included
        _ = ExhibitFactory()

        response = self.client.get(f"/api/v1/exhibits/?owner=99999")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        assert data["count"] == 0
        assert data["results"] == []

        response = self.client.get(f"/api/v1/exhibits/?owner=invalid")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        assert data["count"] == 0
        assert data["results"] == []

        response = self.client.get(f"/api/v1/exhibits/?owner=")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        assert data["count"] == 0
        assert data["results"] == []
