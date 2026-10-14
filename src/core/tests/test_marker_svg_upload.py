from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from core.marker_utils import (
    MAX_SVG_ASPECT_RATIO,
    SVG_RASTER_WIDTH,
    SvgAspectRatioError,
    rasterize_svg,
)
from core.models import Marker
from core.tests.utils import (
    SQUARE_SVG,
    gif_upload,
    make_svg,
    pdf_upload,
    svg_upload,
)
from users.models import User


def raster_size(svg_bytes):
    with Image.open(BytesIO(rasterize_svg(svg_bytes))) as image:
        return image.size


class TestRasterizeSvg:
    def test_a_square_svg_rasterises_at_the_full_width(self):
        assert raster_size(SQUARE_SVG) == (SVG_RASTER_WIDTH, SVG_RASTER_WIDTH)

    def test_a_tall_svg_is_scaled_to_fit_the_height(self):
        assert raster_size(make_svg(100, 400)) == (256, SVG_RASTER_WIDTH)

    def test_a_wide_svg_is_scaled_to_fit_the_width(self):
        assert raster_size(make_svg(400, 100)) == (SVG_RASTER_WIDTH, 256)

    def test_a_tiny_svg_is_scaled_up(self):
        assert raster_size(make_svg(2, 1)) == (SVG_RASTER_WIDTH, 512)

    def test_the_size_falls_back_to_the_viewbox(self):
        assert raster_size(make_svg(viewbox="0 0 50 200")) == (256, SVG_RASTER_WIDTH)

    def test_relative_sizes_fall_back_to_the_viewbox(self):
        svg = make_svg("100%", "100%", viewbox="0 0 200 50")
        assert raster_size(svg) == (SVG_RASTER_WIDTH, 256)

    def test_units_are_converted_before_comparing_the_sides(self):
        # 1in is 96px, so this is square despite the different numbers.
        assert raster_size(make_svg("1in", "96px")) == (
            SVG_RASTER_WIDTH,
            SVG_RASTER_WIDTH,
        )

    def test_the_largest_accepted_ratio_still_rasterises(self):
        svg = make_svg(1, MAX_SVG_ASPECT_RATIO)
        assert raster_size(svg) == (
            round(SVG_RASTER_WIDTH / MAX_SVG_ASPECT_RATIO),
            SVG_RASTER_WIDTH,
        )

    @pytest.mark.parametrize(
        "svg",
        [
            make_svg(10, 100000),
            make_svg(100000, 10),
            make_svg(1, MAX_SVG_ASPECT_RATIO + 0.1),
            make_svg(viewbox="0 0 10 100000"),
            make_svg(width=10, viewbox="0 0 100000 100000"),
        ],
    )
    def test_an_extreme_aspect_ratio_is_rejected(self, svg):
        with pytest.raises(SvgAspectRatioError):
            rasterize_svg(svg)

    @pytest.mark.parametrize(
        "svg",
        [
            make_svg(),
            make_svg(0, 0),
            make_svg(-10, 10),
            make_svg(viewbox="0 0 0 100"),
        ],
    )
    def test_an_svg_without_a_usable_size_is_rejected(self, svg):
        with pytest.raises(ValueError, match="Could not render SVG"):
            rasterize_svg(svg)


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

    def test_a_tall_svg_is_stored_within_the_raster_size(self):
        response = self.upload(svg_upload(content=make_svg(100, 400)))

        assert response.status_code == 302
        marker = Marker.objects.get(title="svg marker")
        with Image.open(marker.source) as image:
            assert image.size == (256, SVG_RASTER_WIDTH)

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

    def test_a_gif_upload_still_creates_the_marker(self):
        response = self.upload(gif_upload())

        assert response.status_code == 302
        marker = Marker.objects.get(title="svg marker")
        assert marker.source.name.endswith(".gif")
        assert marker.marker_img.name == f"markers/{marker.pk}/marker.png"

    def test_a_pdf_is_rejected_with_a_message(self):
        response = self.upload(pdf_upload())

        assert response.status_code == 200
        assert not Marker.objects.exists()
        assert "Upload a valid image" in response.content.decode()

    def test_an_svg_with_an_extreme_aspect_ratio_is_rejected(self):
        response = self.upload(svg_upload(content=make_svg(10, 100000)))

        assert response.status_code == 200
        assert not Marker.objects.exists()
        assert "too long and thin to work as a marker" in response.content.decode()
