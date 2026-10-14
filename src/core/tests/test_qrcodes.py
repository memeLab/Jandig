"""
Exhibits and artworks show a QR code pointing at their public URL, on the
host the visitor is on and always over https (#810, #822), and offer it as a
download for printing.
"""

from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from core import qrcodes
from core.tests.factory import ArtworkFactory, ExhibitFactory


class TestExhibitDetailQrCode(TestCase):
    def setUp(self):
        self.exhibit = ExhibitFactory(slug="my-exhibit")

    def detail(self, host):
        response = self.client.get(
            reverse("exhibit-detail"), {"id": self.exhibit.id}, HTTP_HOST=host
        )
        assert response.status_code == 200
        return response.content.decode()

    def test_the_page_shows_the_qr_code_of_the_exhibit_url(self):
        html = self.detail("dev.jandig.app")

        expected = qrcodes.inline_svg("https://dev.jandig.app/my-exhibit/")
        assert str(expected) in html

    def test_the_qr_code_follows_the_current_host_over_https(self):
        with patch("core.qrcodes.segno.make", wraps=qrcodes.segno.make) as make:
            self.detail("jandig.app")

        make.assert_called_once_with("https://jandig.app/my-exhibit/", micro=False)

    def test_the_page_links_to_the_downloads(self):
        html = self.detail("dev.jandig.app")

        assert 'href="/qrcode/exhibit/my-exhibit.png"' in html
        assert 'href="/qrcode/exhibit/my-exhibit.svg"' in html


class TestArtworkModalQrCode(TestCase):
    def setUp(self):
        self.artwork = ArtworkFactory()

    def modal(self, host):
        response = self.client.get(
            f"/api/v1/artworks/{self.artwork.id}/",
            {"format": "modal"},
            HTTP_HOST=host,
        )
        assert response.status_code == 200
        return response.content.decode()

    def test_the_modal_shows_the_qr_code_of_the_artwork_url(self):
        html = self.modal("dev.jandig.app")

        expected = qrcodes.inline_svg(
            f"https://dev.jandig.app/artwork/?id={self.artwork.id}"
        )
        assert str(expected) in html

    def test_the_qr_code_follows_the_current_host_over_https(self):
        with patch("core.qrcodes.segno.make", wraps=qrcodes.segno.make) as make:
            self.modal("jandig.app")

        make.assert_called_once_with(
            f"https://jandig.app/artwork/?id={self.artwork.id}", micro=False
        )

    def test_the_modal_links_to_the_downloads(self):
        html = self.modal("dev.jandig.app")

        assert f'href="/qrcode/artwork/{self.artwork.id}.png"' in html
        assert f'href="/qrcode/artwork/{self.artwork.id}.svg"' in html


class TestExhibitQrCodeDownload(TestCase):
    def setUp(self):
        self.exhibit = ExhibitFactory(slug="my-exhibit")

    def download(self, file_format, slug="my-exhibit"):
        return self.client.get(
            f"/qrcode/exhibit/{slug}.{file_format}", HTTP_HOST="dev.jandig.app"
        )

    def test_png_download(self):
        response = self.download("png")

        assert response.status_code == 200
        assert response["Content-Type"] == "image/png"
        assert (
            response["Content-Disposition"]
            == 'attachment; filename="jandig-my-exhibit-qrcode.png"'
        )
        assert response.content == qrcodes.render(
            "https://dev.jandig.app/my-exhibit/", "png"
        )

    def test_svg_download(self):
        response = self.download("svg")

        assert response.status_code == 200
        assert response["Content-Type"] == "image/svg+xml"
        assert (
            response["Content-Disposition"]
            == 'attachment; filename="jandig-my-exhibit-qrcode.svg"'
        )
        assert response.content == qrcodes.render(
            "https://dev.jandig.app/my-exhibit/", "svg"
        )

    def test_unknown_exhibit_is_404(self):
        assert self.download("png", slug="no-such-exhibit").status_code == 404

    def test_unknown_format_is_404(self):
        assert self.download("gif").status_code == 404


class TestArtworkQrCodeDownload(TestCase):
    def setUp(self):
        self.artwork = ArtworkFactory()

    def download(self, file_format, artwork_id=None):
        artwork_id = self.artwork.id if artwork_id is None else artwork_id
        return self.client.get(
            f"/qrcode/artwork/{artwork_id}.{file_format}", HTTP_HOST="jandig.app"
        )

    def test_png_download(self):
        response = self.download("png")

        assert response.status_code == 200
        assert response["Content-Type"] == "image/png"
        assert (
            response["Content-Disposition"]
            == f'attachment; filename="jandig-artwork-{self.artwork.id}-qrcode.png"'
        )
        assert response.content == qrcodes.render(
            f"https://jandig.app/artwork/?id={self.artwork.id}", "png"
        )

    def test_svg_download(self):
        response = self.download("svg")

        assert response.status_code == 200
        assert response["Content-Type"] == "image/svg+xml"
        assert (
            response["Content-Disposition"]
            == f'attachment; filename="jandig-artwork-{self.artwork.id}-qrcode.svg"'
        )

    def test_unknown_artwork_is_404(self):
        assert (
            self.download("png", artwork_id=self.artwork.id + 1000).status_code == 404
        )

    def test_non_numeric_id_is_404(self):
        assert self.download("png", artwork_id="abc").status_code == 404


class TestQrCodeRobots(TestCase):
    def test_robots_keep_crawlers_off_the_downloads(self):
        response = self.client.get(reverse("robots_txt"), HTTP_HOST="jandig.app")

        assert "Disallow: /qrcode/" in response.content.decode()
