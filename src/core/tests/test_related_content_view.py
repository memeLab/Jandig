from django.test import TestCase
from django.urls import reverse

from core.tests.factory import (
    ArtworkFactory,
    ExhibitFactory,
    MarkerFactory,
    ObjectFactory,
)


class TestRelatedContentView(TestCase):
    def test_invalid_type(self):
        response = self.client.get(
            reverse("related-content"), {"id": 1, "type": "invalid"}
        )
        assert "artworks" not in response.context
        assert "exhibits" not in response.context

    def test_object_related_content(self):
        # Create object first
        obj = ObjectFactory()
        # Create artworks that references the object
        artwork1 = ArtworkFactory(augmented=obj)
        artwork2 = ArtworkFactory(augmented=obj)
        artwork3 = ArtworkFactory(augmented=obj)

        # Create exhibits and add artworks to it
        exhibit1 = ExhibitFactory(artworks=[artwork1, artwork2])
        exhibit2 = ExhibitFactory(artworks=[artwork3])
        exhibit3 = ExhibitFactory(artworks=[artwork1, artwork3])

        response = self.client.get(
            reverse("related-content"), {"id": obj.id, "type": "object"}
        )
        assert artwork1 in list(response.context["artworks"])
        assert artwork2 in list(response.context["artworks"])
        assert artwork3 in list(response.context["artworks"])
        assert exhibit1 in list(response.context["exhibits"])
        assert exhibit2 in list(response.context["exhibits"])
        assert exhibit3 in list(response.context["exhibits"])
        assert len(response.context["artworks"]) == 3
        assert len(response.context["exhibits"]) == 3

    def test_marker_related_content(self):
        # Create marker first
        marker = MarkerFactory()

        # Create artworks that references the marker
        artwork1 = ArtworkFactory(marker=marker)
        artwork2 = ArtworkFactory(marker=marker)
        artwork3 = ArtworkFactory(marker=marker)

        # Create exhibits and add artworks to it
        exhibit1 = ExhibitFactory(artworks=[artwork1, artwork2])
        exhibit2 = ExhibitFactory(artworks=[artwork3])
        exhibit3 = ExhibitFactory(artworks=[artwork1, artwork3])

        response = self.client.get(
            reverse("related-content"), {"id": marker.id, "type": "marker"}
        )
        assert artwork1 in list(response.context["artworks"])
        assert artwork2 in list(response.context["artworks"])
        assert artwork3 in list(response.context["artworks"])
        assert exhibit1 in list(response.context["exhibits"])
        assert exhibit2 in list(response.context["exhibits"])
        assert exhibit3 in list(response.context["exhibits"])
        assert len(response.context["artworks"]) == 3
        assert len(response.context["exhibits"]) == 3

    def test_artwork_related_content(self):
        artwork = ArtworkFactory()
        # Create exhibits that references the artwork
        exhibit1 = ExhibitFactory(artworks=[artwork])
        exhibit2 = ExhibitFactory(artworks=[artwork])
        exhibit3 = ExhibitFactory(artworks=[artwork])

        response = self.client.get(
            reverse("related-content"), {"id": artwork.id, "type": "artwork"}
        )
        assert list(response.context["exhibits"]) == [exhibit1, exhibit2, exhibit3]
