from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from core.marker_utils import SVG_RASTER_WIDTH
from core.models import Marker
from users.models import User

SQUARE_SVG = b"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
  <rect width="100" height="100" fill="white"/>
  <circle cx="50" cy="50" r="30" fill="black"/>
</svg>
"""


def svg_upload(name="marker.svg", content=SQUARE_SVG):
    return SimpleUploadedFile(name, content, content_type="image/svg+xml")


class TestSvgMarkerUpload(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "testpassword"
        User.objects.create_user(username=self.username, password=self.password)
        self.client.login(username=self.username, password=self.password)

    def upload(self, source, title="svg marker"):
        return self.client.post(
            reverse("marker-upload"),
            {"source": source, "title": title, "author": "Test Author"},
        )

    def test_an_svg_upload_creates_the_marker(self):
        response = self.upload(svg_upload())

        assert response.status_code == 302
        assert Marker.objects.filter(title="svg marker").exists()

    def test_the_svg_is_stored_rasterised_as_png(self):
        self.upload(svg_upload())
        marker = Marker.objects.get(title="svg marker")

        assert marker.source.name.endswith(".png")
        with Image.open(marker.source) as image:
            assert image.format == "PNG"
            assert image.size == (SVG_RASTER_WIDTH, SVG_RASTER_WIDTH)

    def test_the_marker_variants_are_generated_from_the_raster(self):
        self.upload(svg_upload())
        marker = Marker.objects.get(title="svg marker")

        assert marker.marker_img.name == f"markers/{marker.pk}/marker.png"
        assert marker.print_img.name == f"markers/{marker.pk}/print.png"
        assert marker.thumb_img.name == f"markers/{marker.pk}/thumb.png"
        assert marker.file_size > 0

    def test_the_extension_check_ignores_case(self):
        response = self.upload(svg_upload(name="MARKER.SVG"))

        assert response.status_code == 302
        assert Marker.objects.get(title="svg marker").source.name.endswith(".png")

    def test_a_broken_svg_is_rejected_with_a_message(self):
        response = self.upload(svg_upload(content=b"<svg><rect"))

        assert response.status_code == 200
        assert not Marker.objects.exists()
        assert "Could not render SVG" in response.content.decode()

    def test_a_file_that_is_not_an_image_is_rejected(self):
        not_an_image = SimpleUploadedFile(
            "marker.png", b"just some text", content_type="image/png"
        )
        response = self.upload(not_an_image)

        assert response.status_code == 200
        assert not Marker.objects.exists()
        assert "Upload a valid image" in response.content.decode()
