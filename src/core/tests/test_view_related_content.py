from django.test import TestCase
from django.urls import reverse

from core.models import Exhibit
from core.tests.factory import (
    ArtworkFactory,
    MarkerFactory,
    ObjectFactory,
)
from users.tests.factory import ProfileFactory


def create_ar_exhibit(artworks):
    """Create an AR exhibit with specific artworks, bypassing factory randomness."""
    exhibit = Exhibit.objects.create(
        owner=ProfileFactory(),
        name=f"Exhibit {Exhibit.objects.count() + 1}",
        slug=f"exhibit-{Exhibit.objects.count() + 1}",
        exhibit_type="AR",
    )
    exhibit.artworks.set(artworks)
    return exhibit


class TestRelatedContentView(TestCase):
    def test_invalid_type(self):
        response = self.client.get(
            reverse("related-content"), {"id": 1, "type": "invalid"}
        )
        assert response.status_code == 404
        response = self.client.get(
            reverse("related-content"), {"id": "aaaa", "type": "object"}
        )
        assert response.status_code == 404
        response = self.client.get(reverse("related-content"), {"id": 1, "type": ""})
        assert response.status_code == 404
        response = self.client.get(reverse("related-content"), {"id": 1})
        assert response.status_code == 404
        response = self.client.get(reverse("related-content"), {"type": "object"})
        assert response.status_code == 404
        response = self.client.get(reverse("related-content"), {})
        assert response.status_code == 404
        response = self.client.get(
            reverse("related-content"), {"id": "", "type": "object"}
        )
        assert response.status_code == 404
        response = self.client.get(reverse("related-content"), {"id": 1, "type": 1})
        assert response.status_code == 404

    def test_object_related_content(self):
        # Create object first
        obj = ObjectFactory()
        # Create artworks that references the object
        artwork1 = ArtworkFactory(augmented=obj)
        artwork2 = ArtworkFactory(augmented=obj)
        artwork3 = ArtworkFactory(augmented=obj)

        # Create exhibits and add artworks to it
        exhibit1 = create_ar_exhibit([artwork1, artwork2])
        exhibit2 = create_ar_exhibit([artwork3])
        exhibit3 = create_ar_exhibit([artwork1, artwork3])

        response = self.client.get(
            reverse("related-content"), {"id": obj.id, "type": "object"}
        )
        assert artwork1 in list(response.context["artworks"])
        assert artwork2 in list(response.context["artworks"])
        assert artwork3 in list(response.context["artworks"])
        assert exhibit1 in list(response.context["ar_exhibits"])
        assert exhibit2 in list(response.context["ar_exhibits"])
        assert exhibit3 in list(response.context["ar_exhibits"])
        assert len(response.context["artworks"]) == 3
        assert len(response.context["ar_exhibits"]) == 3

    def test_marker_related_content(self):
        # Create marker first
        marker = MarkerFactory()

        # Create artworks that references the marker
        artwork1 = ArtworkFactory(marker=marker)
        artwork2 = ArtworkFactory(marker=marker)
        artwork3 = ArtworkFactory(marker=marker)

        # Create exhibits and add artworks to it
        exhibit1 = create_ar_exhibit([artwork1, artwork2])
        exhibit2 = create_ar_exhibit([artwork3])
        exhibit3 = create_ar_exhibit([artwork1, artwork3])

        response = self.client.get(
            reverse("related-content"), {"id": marker.id, "type": "marker"}
        )
        assert artwork1 in list(response.context["artworks"])
        assert artwork2 in list(response.context["artworks"])
        assert artwork3 in list(response.context["artworks"])
        assert exhibit1 in list(response.context["ar_exhibits"])
        assert exhibit2 in list(response.context["ar_exhibits"])
        assert exhibit3 in list(response.context["ar_exhibits"])
        assert len(response.context["artworks"]) == 3
        assert len(response.context["ar_exhibits"]) == 3

    def test_artwork_related_content(self):
        artwork = ArtworkFactory()
        # Create exhibits that references the artwork
        exhibit1 = create_ar_exhibit([artwork])
        exhibit2 = create_ar_exhibit([artwork])
        exhibit3 = create_ar_exhibit([artwork])

        response = self.client.get(
            reverse("related-content"), {"id": artwork.id, "type": "artwork"}
        )
        assert list(response.context["ar_exhibits"]) == [exhibit1, exhibit2, exhibit3]
