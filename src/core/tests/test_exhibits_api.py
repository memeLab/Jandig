"""Test using the exhibit API for Jandig Exhibit"""

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from core.serializers import ArtworkSerializer
from core.tests.factory import ExhibitFactory
from users.tests.factory import ProfileFactory, UserFactory

fake_file = SimpleUploadedFile("fake_file.png", b"these are the file contents!")


class TestExhibitAPI(TestCase):
    def setUp(self):
        self.user = UserFactory(username="testuserexhibit")
        self.profile = ProfileFactory(user=self.user)

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
        exhibit = ExhibitFactory(owner=self.profile, name="test")
        response = self.client.get("/api/v1/exhibits/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["id"] == exhibit.id
        assert data["results"][0]["name"] == exhibit.name
        assert data["results"][0]["slug"] == exhibit.slug
        assert data["results"][0]["owner"] == self.profile.id
        assert (
            data["results"][0]["artworks"]
            == ArtworkSerializer(exhibit.artworks.all(), many=True).data
        )

    def test_api_exhibit_lists_multiple_exhibits(self):
        """API returns multiple exhibits if there are multiple exhibits"""
        for i in range(0, settings.PAGE_SIZE + 1):
            ExhibitFactory(owner=self.profile, name=f"name_{i}", slug=f"slug_{i}")
        response = self.client.get("/api/v1/exhibits/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        assert data["count"] == settings.PAGE_SIZE + 1
        assert (
            data["next"]
            == f"http://testserver/api/v1/exhibits/?limit={settings.PAGE_SIZE}&offset={settings.PAGE_SIZE}"
        )

    def test_retrieve_exhibit_by_id(self):
        """Test that the exhibit can be retrieved using its ID on the API path"""
        exhibit = ExhibitFactory(owner=self.profile, name="test")
        response = self.client.get(f"/api/v1/exhibits/{str(exhibit.id)}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        assert data["id"] == exhibit.id
        assert data["name"] == exhibit.name
        assert data["slug"] == exhibit.slug
        assert data["owner"] == self.profile.id
        assert (
            data["artworks"]
            == ArtworkSerializer(exhibit.artworks.all(), many=True).data
        )

    def test_searching_exhibits_by_owner_id(self):
        """Test that the exhibit can be searched using owner id"""
        exhibit = ExhibitFactory(owner=self.profile)

        # Extra exhibit from another owner to check if it is not included
        _ = ExhibitFactory()

        response = self.client.get(f"/api/v1/exhibits/?owner={self.profile.user.id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["id"] == exhibit.id
        assert data["results"][0]["name"] == exhibit.name
        assert data["results"][0]["slug"] == exhibit.slug
        assert data["results"][0]["owner"] == self.profile.user.id
        assert (
            data["results"][0]["artworks"]
            == ArtworkSerializer(exhibit.artworks.all(), many=True).data
        )

    def test_searching_exhibits_by_invalid_owner(self):
        """Test that the exhibit cannot be searched using invalid owner id"""

        response = self.client.get("/api/v1/exhibits/?owner=99999")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        assert data["count"] == 0
        assert data["results"] == []

        response = self.client.get("/api/v1/exhibits/?owner=invalid")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        assert data["count"] == 0
        assert data["results"] == []

        response = self.client.get("/api/v1/exhibits/?owner=")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        assert data["count"] == 0
        assert data["results"] == []

    def test_searching_exhibits_by_name(self):
        """Test that the exhibit can be searched using name"""
        exhibit = ExhibitFactory(owner=self.profile, name="test")
        response = self.client.get("/api/v1/exhibits/?search=test")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["id"] == exhibit.id
        assert data["results"][0]["name"] == exhibit.name
        assert data["results"][0]["slug"] == exhibit.slug
        assert data["results"][0]["owner"] == self.profile.id

    def test_searching_by_name_filters_exhibits(self):
        """Test that the exhibit API filters results using name"""
        exhibit = ExhibitFactory(owner=self.profile, name="test")
        ExhibitFactory(owner=self.profile, name="not similar 2")
        ExhibitFactory(owner=self.profile, name="not similar 3")
        response = self.client.get("/api/v1/exhibits/?search=test")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["id"] == exhibit.id
        assert data["results"][0]["name"] == exhibit.name
        assert data["results"][0]["slug"] == exhibit.slug
        assert data["results"][0]["owner"] == self.profile.id

    def test_searching_by_name_with_special_characters(self):
        """Test that the exhibit API filters results using name with special characters"""
        exhibit = ExhibitFactory(
            owner=self.profile, name="test@#$%^&*() ação pátio câmara índio"
        )

        response = self.client.get("/api/v1/exhibits/?search=test@")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["id"] == exhibit.id
        assert data["results"][0]["name"] == exhibit.name
        assert data["results"][0]["slug"] == exhibit.slug
        assert data["results"][0]["owner"] == self.profile.id

        response = self.client.get("/api/v1/exhibits/?search=() a")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["id"] == exhibit.id
        assert data["results"][0]["name"] == exhibit.name
        assert data["results"][0]["slug"] == exhibit.slug
        assert data["results"][0]["owner"] == self.profile.id

        response = self.client.get("/api/v1/exhibits/?search=ação pátio")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["id"] == exhibit.id
        assert data["results"][0]["name"] == exhibit.name
        assert data["results"][0]["slug"] == exhibit.slug
        assert data["results"][0]["owner"] == self.profile.id

    def test_searching_exhibits_by_invalid_name(self):
        """Test that the exhibit cannot be searched using invalid name"""
        _ = ExhibitFactory(owner=self.profile, name="test")
        response = self.client.get("/api/v1/exhibits/?search=invalid")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        assert data["count"] == 0
        assert data["results"] == []

    def test_search_with_owner_and_name(self):
        """Test that the exhibit can be searched using owner id and name"""
        exhibit = ExhibitFactory(owner=self.profile, name="test")
        _ = ExhibitFactory(name="not similar 2")
        _ = ExhibitFactory(owner=self.profile, name="not similar 3")
        response = self.client.get(
            f"/api/v1/exhibits/?owner={self.profile.user.id}&search=test"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["id"] == exhibit.id
        assert data["results"][0]["name"] == exhibit.name
        assert data["results"][0]["slug"] == exhibit.slug
        assert data["results"][0]["owner"] == self.profile.id
