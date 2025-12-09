"""Test using the marker API for Jandig Markers"""

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from users.models import User

fake_file = SimpleUploadedFile("fake_file.png", b"these are the file contents!")

EXAMPLE_MARKER_PATH = "src/core/tests/test_files/example_marker_500x500.jpg"


class TestGenerateMarkerAPI(TestCase):
    def setUp(self):
        self.user = User.objects.create()
        self.profile = self.user.profile

    def test_get_does_not_work(self):
        response = self.client.get(reverse("markergenerator"))
        assert response.status_code == 405

    def test_post_no_file(self):
        response = self.client.post(reverse("markergenerator"), {})
        assert response.status_code == 400
        assert response.data["error"] == "No image provided."

    def test_post_with_file(self):
        with open(EXAMPLE_MARKER_PATH, "rb") as image_file:
            data = {"source": image_file, "inner_border": "true"}
            response = self.client.post(reverse("markergenerator"), data)
        assert response.status_code == 200
        assert "data:image/jpeg;base64," in response.content.decode()
        assert len(response.content) > 1000  # Ensure some content is returned
        assert response.content.decode().startswith("<img src=")
