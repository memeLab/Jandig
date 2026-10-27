import io

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from core.forms import MAX_MARKER_DIMENSION, UploadMarkerForm
from core.marker_utils import SVG_RASTER_WIDTH
from core.models import Marker
from users.models import User


def build_png(width, height):
    """Generate a PNG upload of the given size without touching the repository."""
    buffer = io.BytesIO()
    Image.new("RGB", (width, height), "white").save(buffer, format="PNG")
    buffer.seek(0)
    return SimpleUploadedFile(
        f"marker_{width}x{height}.png", buffer.read(), content_type="image/png"
    )


class TestMarkerResolutionLimit(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "testpassword"
        User.objects.create_user(username=self.username, password=self.password)

    def test_form_rejects_marker_wider_than_the_limit(self):
        form = UploadMarkerForm(
            data={"title": "Too wide", "author": "Test Author"},
            files={"source": build_png(MAX_MARKER_DIMENSION + 1, 10)},
        )

        assert not form.is_valid()
        assert "source" in form.errors
        assert str(MAX_MARKER_DIMENSION) in form.errors["source"][0]

    def test_form_rejects_marker_taller_than_the_limit(self):
        form = UploadMarkerForm(
            data={"title": "Too tall", "author": "Test Author"},
            files={"source": build_png(10, MAX_MARKER_DIMENSION + 1)},
        )

        assert not form.is_valid()
        assert "source" in form.errors

    def test_form_accepts_a_marker_exactly_at_the_limit(self):
        form = UploadMarkerForm(
            data={"title": "At the limit", "author": "Test Author"},
            files={"source": build_png(MAX_MARKER_DIMENSION, MAX_MARKER_DIMENSION)},
        )

        assert form.is_valid(), form.errors

    def test_form_accepts_an_ordinary_marker(self):
        form = UploadMarkerForm(
            data={"title": "Normal", "author": "Test Author"},
            files={"source": build_png(500, 500)},
        )

        assert form.is_valid(), form.errors

    def test_form_fits_a_tall_svg_within_the_limit(self):
        # At a fixed raster width this 1:5 SVG used to grow to 1024x5120 and
        # trip the limit. The raster is now fitted by its longest side, so no
        # SVG the aspect-ratio check lets through can get anywhere near it.
        tall_svg = (
            b'<svg xmlns="http://www.w3.org/2000/svg" width="100" height="500">'
            b'<rect width="100" height="500" fill="white"/></svg>'
        )
        form = UploadMarkerForm(
            data={"title": "Tall SVG", "author": "Test Author"},
            files={
                "source": SimpleUploadedFile(
                    "tall.svg", tall_svg, content_type="image/svg+xml"
                )
            },
        )

        assert form.is_valid(), form.errors
        with Image.open(form.cleaned_data["source"]) as image:
            assert image.size == (205, SVG_RASTER_WIDTH)
        assert SVG_RASTER_WIDTH <= MAX_MARKER_DIMENSION

    def test_upload_view_rejects_an_oversized_marker(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(
            reverse("marker-upload"),
            {
                "title": "Way too big",
                "author": "Test Author",
                "source": build_png(MAX_MARKER_DIMENSION + 1, MAX_MARKER_DIMENSION + 1),
            },
        )

        # The form is redisplayed with the error instead of redirecting.
        assert response.status_code == 200
        assert not Marker.objects.filter(title="Way too big").exists()
