from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from core.models import Artwork, Marker, Object


class TestTryJandigPreview(TestCase):
    def test_try_jandig_preview_renders_ar_template(self):
        url = reverse("try-jandig-preview")
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        self.assertTemplateUsed(response, "core/ar.jinja2")

    def test_try_jandig_preview_uses_static_artwork_dict(self):
        url = reverse("try-jandig-preview")
        response = self.client.get(url)
        artworks = response.context["artworks"]
        assert len(artworks) == 1

        artwork = artworks[0]
        assert artwork["marker"]["marker_img"]["url"].endswith(
            "try_jandig_marker.png"
        )
        assert artwork["augmented"]["file_extension"] == "gif"
        assert artwork["augmented"]["spritesheet_file"]["url"].endswith(
            "try_jandig_object_spritesheet.png"
        )
        assert artwork["augmented"]["spritesheet_metadata"]["url"].endswith(
            "try_jandig_object_spritesheet.json"
        )

    def test_try_jandig_preview_does_not_create_db_rows(self):
        url = reverse("try-jandig-preview")
        self.client.get(url)
        assert Marker.objects.count() == 0
        assert Object.objects.count() == 0
        assert Artwork.objects.count() == 0
