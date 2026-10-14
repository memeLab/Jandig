"""Test using the marker API for Jandig Markers"""

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from core.tests.utils import make_svg
from users.models import User

fake_file = SimpleUploadedFile("fake_file.png", b"these are the file contents!")

EXAMPLE_MARKER_PATH = "src/core/tests/test_files/example_marker_500x500.jpg"

SQUARE_SVG = (
    b'<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">'
    b'<rect width="100" height="100" fill="white"/>'
    b'<circle cx="50" cy="50" r="30" fill="black"/></svg>'
)


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
        assert "data:image/png;base64," in response.content.decode()
        assert len(response.content) > 1000  # Ensure some content is returned
        assert response.content.decode().startswith("<img src=")

    def test_post_with_svg_returns_a_preview(self):
        svg = SimpleUploadedFile("marker.svg", SQUARE_SVG, content_type="image/svg+xml")
        response = self.client.post(reverse("markergenerator"), {"source": svg})
        assert response.status_code == 200
        assert response.content.decode().startswith("<img src=")
        assert "data:image/png;base64," in response.content.decode()

    def test_post_with_broken_svg_is_a_client_error(self):
        svg = SimpleUploadedFile(
            "marker.svg", b"<svg><rect", content_type="image/svg+xml"
        )
        response = self.client.post(reverse("markergenerator"), {"source": svg})
        assert response.status_code == 400
        assert response.data["error"].startswith("Could not render SVG")

    def test_post_with_a_file_that_is_not_an_image_is_a_client_error(self):
        not_an_image = SimpleUploadedFile("marker.png", b"just some text")
        response = self.client.post(
            reverse("markergenerator"), {"source": not_an_image}
        )
        assert response.status_code == 400
        assert response.data["error"].startswith("Upload a valid image")

    def test_post_with_tall_svg_returns_a_preview(self):
        svg = SimpleUploadedFile(
            "marker.svg", make_svg(100, 400), content_type="image/svg+xml"
        )
        response = self.client.post(reverse("markergenerator"), {"source": svg})
        assert response.status_code == 200
        assert "data:image/png;base64," in response.content.decode()

    def test_post_with_extreme_aspect_ratio_svg_is_a_client_error(self):
        svg = SimpleUploadedFile(
            "marker.svg", make_svg(10, 100000), content_type="image/svg+xml"
        )
        response = self.client.post(reverse("markergenerator"), {"source": svg})
        assert response.status_code == 400
        assert response.data["error"].startswith("This SVG is too long and thin")
