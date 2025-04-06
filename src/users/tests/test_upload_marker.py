from django.urls import reverse
from rest_framework import status
from django.test import TestCase

from core.models import Marker
from users.models import User

EXAMPLE_MARKER_PATH = "src/users/tests/test_files/example_marker_500x500.jpg"
EXAMPLE_MARKER_SIZE = 18403  # Size in bytes of the example marker image


class TestMarkerUpload(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "testpassword"
        User.objects.create_user(
            username=self.username,
            password=self.password,
            is_staff=False,
            is_superuser=False,
        )

    def test_upload_marker_unauthenticated(self):
        url = reverse("marker-upload")
        with open(EXAMPLE_MARKER_PATH, "rb") as image_file:
            data = {"source": image_file, "title": "Test Marker"}
            response = self.client.post(url, data)
        assert response.status_code == status.HTTP_302_FOUND  # Redirect to login page
        assert "/users/login" in response.url

    def test_upload_marker_authenticated(self):
        url = reverse("marker-upload")
        with open(EXAMPLE_MARKER_PATH, "rb") as image_file:
            data = {
                "source": image_file,
                "title": "Test Marker",
                "author": "Test Author",
            }

            self.client.login(username=self.username, password=self.password)
            response = self.client.post(url, data)
        assert response.status_code == status.HTTP_302_FOUND  # Redirect to home page

        # Verify that a Marker instance was created
        assert Marker.objects.count() == 1
        marker = Marker.objects.first()
        assert marker.title == "Test Marker"
        assert marker.author == "Test Author"
        assert marker.file_size == EXAMPLE_MARKER_SIZE
        assert marker.source.name == "markers/example_marker_500x500.jpg"
