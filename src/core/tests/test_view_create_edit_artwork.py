from django.test import TestCase
from django.urls import reverse

from core.models import Artwork
from core.tests.factory import (
    ArtworkFactory,
    MarkerFactory,
    ObjectFactory,
)
from users.tests.factory import ProfileFactory, UserFactory


class TestCreateArtworkView(TestCase):
    def setUp(self):
        self.user = UserFactory(username="testuser")
        self.profile = ProfileFactory(user=self.user)
        self.client.force_login(self.user)
        self.marker = MarkerFactory(author=self.profile)
        self.object = ObjectFactory(author=self.profile)

    def test_create_artwork_success(self):
        url = reverse("create-artwork")
        data = {
            "title": "My Test Artwork",
            "description": "This is a test artwork.",
            "scale": 1.5,
            "position_x": 1,
            "position_y": 1,
            "selected_marker": self.marker.id,
            "selected_object": self.object.id,
        }
        response = self.client.post(url, data)
        # Should redirect to profile after creation
        assert response.status_code == 302
        # Artwork should be created
        assert Artwork.objects.count() == 1
        artwork = Artwork.objects.first()
        assert artwork.title == "My Test Artwork"
        assert artwork.description == "This is a test artwork."
        assert artwork.scale_x == 1.5
        assert artwork.scale_y == 1.5
        assert artwork.position_x == 1
        assert artwork.position_y == 1
        assert artwork.marker == self.marker
        assert artwork.augmented == self.object
        assert artwork.author == self.profile

    def test_create_artwork_requires_login(self):
        self.client.logout()
        url = reverse("create-artwork")
        response = self.client.get(url)
        assert response.status_code == 302  # Should redirect to login
        self.assertRedirects(response, f"{reverse('login')}?next={url}")

        # Valid request data should not be accepted without login
        data = {
            "title": "My Test Artwork",
            "description": "This is a test artwork.",
            "scale": 1.5,
            "position_x": 1,
            "position_y": 1,
            "selected_marker": self.marker.id,
            "selected_object": self.object.id,
        }
        response = self.client.post(url, data)
        assert response.status_code == 302  # Should redirect to login
        self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_create_exhibit_invalid_data(self):
        url = reverse("create-artwork")
        data = {
            "title": "My Test Artwork",
            "description": "This is a test artwork.",
            "scale": 1.5,
            "position_x": 1,
            "position_y": 1,
            # "selected_marker": self.marker.id,
            "selected_object": self.object.id,
        }
        response = self.client.post(url, data)
        # Should not redirect, should show form again
        assert response.status_code == 200
        assert "form" in response.content.decode()
        assert Artwork.objects.count() == 0  # No artwork should be created

        data = {
            "title": "",  # Empty title
            "description": "This is a test artwork.",
            "scale": 1.5,
            "position_x": 1,
            "position_y": 1,
            "selected_marker": self.marker.id,
            "selected_object": self.object.id,
        }
        response = self.client.post(url, data)
        # Should not redirect, should show form again
        assert response.status_code == 200
        assert "form" in response.content.decode()
        assert Artwork.objects.count() == 0  # No artwork should be created
        del data["title"]  # Remove title to test required field
        response = self.client.post(url, data)
        # Should not redirect, should show form again
        assert response.status_code == 200
        assert "form" in response.content.decode()
        assert Artwork.objects.count() == 0  # No artwork should be created

        data = {
            "title": "My Test Artwork",
            "description": "This is a test artwork.",
            "scale": 1.5,
            "position_x": 1,
            "position_y": 1,
            "selected_marker": self.marker.id,
            # "selected_object": self.object.id,  # Missing object
        }
        response = self.client.post(url, data)
        # Should not redirect, should show form again
        assert response.status_code == 200
        assert "form" in response.content.decode()
        assert Artwork.objects.count() == 0  # No artwork should be created


class TestEditArtworkView(TestCase):
    def setUp(self):
        self.user = UserFactory(username="testuser")
        self.profile = ProfileFactory(user=self.user)
        self.client.force_login(self.user)
        self.marker = MarkerFactory(author=self.profile)
        self.object = ObjectFactory(author=self.profile)
        self.artwork = ArtworkFactory(
            author=self.profile,
            marker=self.marker,
            augmented=self.object,
            title="Original Artwork",
            description="Original Description",
            scale_x=1.0,
            scale_y=1.0,
            position_x=0,
            position_y=0,
        )

    def test_edit_artwork_requires_login(self):
        self.client.logout()
        url = reverse("edit-artwork") + f"?id={self.artwork.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

        # Valid request data should not be accepted without login
        data = {
            "title": "My Test Artwork",
            "description": "This is a test artwork.",
            "scale": 1.5,
            "position_x": 1,
            "position_y": 1,
            "selected_marker": self.marker.id,
            "selected_object": self.object.id,
        }
        response = self.client.post(url, data)
        assert response.status_code == 302  # Should redirect to login
        self.assertRedirects(response, f"{reverse('login')}?next={url}")

        artwork = Artwork.objects.get(id=self.artwork.id)
        assert artwork.title == "Original Artwork"
        assert artwork.description == "Original Description"
        assert artwork.scale_x == 1.0
        assert artwork.scale_y == 1.0
        assert artwork.position_x == 0
        assert artwork.position_y == 0
        assert artwork.marker == self.marker
        assert artwork.augmented == self.object

    def test_edit_artwork_comes_populated_with_existing_data(self):
        url = reverse("edit-artwork") + f"?id={self.artwork.id}"
        response = self.client.get(url)
        assert response.status_code == 200
        assert "form" in response.context
        form = response.context["form"]
        assert form.initial["title"] == self.artwork.title
        assert form.initial["description"] == self.artwork.description
        assert form.initial["scale"] == self.artwork.scale_x
        assert form.initial["position_x"] == self.artwork.position_x
        assert form.initial["position_y"] == self.artwork.position_y
        assert form.initial["selected_marker"] == self.marker.id
        assert form.initial["selected_object"] == self.object.id

    def test_edit_artwork_success(self):
        url = reverse("edit-artwork") + f"?id={self.artwork.id}"
        data = {
            "title": "Edited Artwork",
            "description": "Edited Description",
            "scale": 2.0,
            "position_x": 2,
            "position_y": 2,
            "selected_marker": self.marker.id,
            "selected_object": self.object.id,
        }
        response = self.client.post(url, data)
        # Should redirect to profile after editing
        assert response.status_code == 302
        self.assertRedirects(response, reverse("profile"))

        # Artwork should be updated
        artwork = Artwork.objects.get(id=self.artwork.id)
        assert artwork.title == "Edited Artwork"
        assert artwork.description == "Edited Description"
        assert artwork.scale_x == 2.0
        assert artwork.scale_y == 2.0
        assert artwork.position_x == 2
        assert artwork.position_y == 2
        assert artwork.marker == self.marker
        assert artwork.augmented == self.object

    def test_edit_artwork_invalid_data(self):
        url = reverse("edit-artwork") + f"?id={self.artwork.id}"
        data = {
            "title": "My Test Artwork",
            "description": "This is a test artwork.",
            "scale": 1.5,
            "position_x": 1,
            "position_y": 1,
            # "selected_marker": self.marker.id,
            "selected_object": self.object.id,
        }
        response = self.client.post(url, data)
        # Should not redirect, should show form again
        assert response.status_code == 200
        assert "form" in response.content.decode()

        data = {
            "title": "",  # Empty title
            "description": "This is a test artwork.",
            "scale": 1.5,
            "position_x": 1,
            "position_y": 1,
            "selected_marker": self.marker.id,
            "selected_object": self.object.id,
        }
        response = self.client.post(url, data)
        # Should not redirect, should show form again
        assert response.status_code == 200
        assert "form" in response.content.decode()
        del data["title"]  # Remove title to test required field
        response = self.client.post(url, data)
        # Should not redirect, should show form again
        assert response.status_code == 200
        assert "form" in response.content.decode()

        data = {
            "title": "My Test Artwork",
            "description": "This is a test artwork.",
            "scale": 1.5,
            "position_x": 1,
            "position_y": 1,
            "selected_marker": self.marker.id,
            # "selected_object": self.object.id,  # Missing object
        }
        response = self.client.post(url, data)
        # Should not redirect, should show form again
        assert response.status_code == 200
        assert "form" in response.content.decode()
