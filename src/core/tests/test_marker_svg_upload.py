import gzip
from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from core import marker_utils
from core.marker_utils import (
    MAX_SVG_ASPECT_RATIO,
    MAX_SVG_LAYER_PIXELS,
    SVG_RASTER_WIDTH,
    SvgAspectRatioError,
    SvgTooComplexError,
    rasterize_svg,
)
from core.models import Marker
from core.tests.utils import (
    SQUARE_SVG,
    data_url,
    gif_upload,
    make_svg,
    pdf_upload,
    png_bytes,
    raster_image_bytes,
    svg_document,
    svg_upload,
    svg_with_image,
)
from users.models import User

# Embedded PNGs this size are a few kilobytes but decode to 100 MB, over the
# MAX_SVG_LAYER_PIXELS budget; small enough not to hurt if a guard regresses.
OVERSIZED_SIDE = 5000
# How many groups can nest on a full-size raster before reaching the budget.
GROUP_DEPTH_LIMIT = MAX_SVG_LAYER_PIXELS // (SVG_RASTER_WIDTH * SVG_RASTER_WIDTH)


def raster_size(svg_bytes):
    with Image.open(BytesIO(rasterize_svg(svg_bytes))) as image:
        return image.size


def centre_pixel(svg_bytes):
    with Image.open(BytesIO(rasterize_svg(svg_bytes))) as image:
        return image.convert("L").getpixel((image.width // 2, image.height // 2))


def nested_groups(depth, attributes='opacity="0.5"'):
    return svg_document(
        f"<g {attributes}>" * depth
        + '<rect width="100" height="100" fill="black"/>'
        + "</g>" * depth
    )


def masked_square(mask_size):
    return svg_document(
        '<defs><mask id="m" maskUnits="userSpaceOnUse" x="0" y="0" '
        f'width="{mask_size}" height="{mask_size}">'
        '<rect width="100" height="100" fill="white"/></mask></defs>'
        '<rect width="100" height="100" fill="black" mask="url(#m)"/>'
    )


def pattern_filled_square(pattern_size):
    return svg_document(
        '<defs><pattern id="p" patternUnits="userSpaceOnUse" '
        f'width="{pattern_size}" height="{pattern_size}">'
        f'<rect width="{pattern_size}" height="{pattern_size}" fill="black"/>'
        "</pattern></defs>"
        '<rect width="100" height="100" fill="url(#p)"/>'
    )


class TestSvgEmbeddedContent:
    """Content inside an SVG that makes cairosvg allocate memory, or spend
    time, independently of the raster size (#1005)."""

    def test_an_embedded_png_is_drawn(self):
        assert centre_pixel(svg_with_image(png_bytes(10, 10))) == 0

    @pytest.mark.parametrize("image_format", ["JPEG", "GIF", "WEBP"])
    def test_other_embedded_raster_formats_are_drawn(self, image_format):
        svg = svg_with_image(
            raster_image_bytes(image_format), mime=f"image/{image_format.lower()}"
        )
        assert centre_pixel(svg) < 16

    def test_an_embedded_svg_is_drawn(self):
        svg = svg_with_image(make_svg(100, 100), mime="image/svg+xml")
        assert centre_pixel(svg) == 0

    def test_an_embedded_png_over_the_pixel_budget_is_rejected(self):
        # cairo decodes embedded PNGs itself, at full size, without Pillow's
        # decompression-bomb check.
        svg = svg_with_image(png_bytes(OVERSIZED_SIDE, OVERSIZED_SIDE))
        with pytest.raises(SvgTooComplexError):
            rasterize_svg(svg)

    def test_an_embedded_jpeg_over_the_pixel_budget_is_rejected(self):
        # Pillow only refuses images above about 179 megapixels.
        jpeg = raster_image_bytes("JPEG", size=(OVERSIZED_SIDE, OVERSIZED_SIDE))
        with pytest.raises(SvgTooComplexError):
            rasterize_svg(svg_with_image(jpeg, mime="image/jpeg"))

    def test_the_pixel_budget_covers_all_embedded_images_together(self, monkeypatch):
        monkeypatch.setattr(marker_utils, "MAX_SVG_LAYER_PIXELS", 150)
        image = png_bytes(10, 10)

        rasterize_svg(svg_with_image(image))
        with pytest.raises(SvgTooComplexError):
            rasterize_svg(svg_with_image(image, copies=2))

    def test_an_image_drawn_again_through_use_counts_again(self, monkeypatch):
        monkeypatch.setattr(marker_utils, "MAX_SVG_LAYER_PIXELS", 150)
        image = f'<image id="i" href="{data_url(png_bytes(10, 10), "image/png")}"/>'

        with pytest.raises(SvgTooComplexError):
            rasterize_svg(svg_document(image + '<use href="#i"/>'))

    def test_an_embedded_image_in_another_format_is_rejected(self):
        svg = svg_with_image(raster_image_bytes("BMP"), mime="image/bmp")
        with pytest.raises(ValueError, match="unsupported BMP"):
            rasterize_svg(svg)

    def test_a_compressed_svg_is_rejected(self):
        with pytest.raises(ValueError, match="compressed"):
            rasterize_svg(gzip.compress(SQUARE_SVG))

    @pytest.mark.parametrize(
        "element",
        [
            '<image href="{href}" width="100" height="100"/>',
            '<use href="{href}"/>',
            '<text y="50"><tref href="{href}"/></text>',
        ],
    )
    def test_compressed_content_inside_an_svg_is_rejected(self, element):
        # cairosvg would gunzip it in one go, however large it expands.
        href = data_url(gzip.compress(SQUARE_SVG), "image/svg+xml")
        with pytest.raises(SvgTooComplexError):
            rasterize_svg(svg_document(element.format(href=href)))

    def test_a_small_mask_is_applied(self):
        assert centre_pixel(masked_square(100)) == 0

    def test_a_mask_layer_over_the_pixel_budget_is_rejected(self):
        # cairo rasterises the mask at the size the SVG declares for it.
        with pytest.raises(SvgTooComplexError):
            rasterize_svg(masked_square(OVERSIZED_SIDE))

    def test_a_small_pattern_is_applied(self):
        assert centre_pixel(pattern_filled_square(10)) == 0

    def test_a_pattern_layer_over_the_pixel_budget_is_rejected(self):
        with pytest.raises(SvgTooComplexError):
            rasterize_svg(pattern_filled_square(OVERSIZED_SIDE))

    def test_groups_nested_up_to_the_budget_are_drawn(self):
        assert raster_size(nested_groups(GROUP_DEPTH_LIMIT)) == (
            SVG_RASTER_WIDTH,
            SVG_RASTER_WIDTH,
        )

    @pytest.mark.parametrize(
        "attributes",
        ['opacity="0.5"', 'mask="url(#m)"', 'filter="url(#f)"'],
    )
    def test_groups_nested_past_the_budget_are_rejected(self, attributes):
        # Each one is a scratch layer as large as the raster.
        with pytest.raises(SvgTooComplexError):
            rasterize_svg(nested_groups(GROUP_DEPTH_LIMIT + 1, attributes))

    def test_a_use_reference_cycle_is_rejected(self):
        # Each round nests one more group layer, until the budget stops it.
        svg = svg_document(
            '<g id="loop" opacity="0.5">'
            '<rect width="10" height="10"/><use href="#loop"/></g>'
        )
        with pytest.raises(SvgTooComplexError):
            rasterize_svg(svg)

    def test_rendering_stops_after_the_time_limit(self, monkeypatch):
        monkeypatch.setattr(marker_utils, "MAX_SVG_RENDER_SECONDS", -1)
        with pytest.raises(SvgTooComplexError):
            rasterize_svg(SQUARE_SVG)


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

    def test_an_svg_too_complex_to_render_is_rejected(self):
        svg = svg_with_image(png_bytes(OVERSIZED_SIDE, OVERSIZED_SIDE))
        response = self.upload(svg_upload(content=svg))

        assert response.status_code == 200
        assert not Marker.objects.exists()
        assert "too complex to turn into a marker" in response.content.decode()

    def test_an_svg_with_a_small_embedded_image_creates_the_marker(self):
        response = self.upload(svg_upload(content=svg_with_image(png_bytes(10, 10))))

        assert response.status_code == 302
        assert Marker.objects.filter(title="svg marker").exists()
