from django.test import TestCase
from django.urls import reverse

from core.models import Artwork, Exhibit, Marker, Object, Sound
from core.tests.factory import MarkerFactory

HIGHLIGHTABLE = (Marker, Object, Artwork, Exhibit, Sound)


class TestHighlightField(TestCase):
    def test_every_listed_content_type_can_be_highlighted(self):
        for model in HIGHLIGHTABLE:
            with self.subTest(model=model.__name__):
                field = model._meta.get_field("highlighted")
                assert field.default is False

    def test_content_is_not_highlighted_by_default(self):
        marker = MarkerFactory()

        assert marker.highlighted is False


class TestHighlightOrdering(TestCase):
    """Highlighted content must lead the listings, regardless of age."""

    def test_highlighted_marker_is_listed_before_newer_ones(self):
        old = MarkerFactory()
        old.highlighted = True
        old.save()
        newest = MarkerFactory()

        response = self.client.get(reverse("collection"))
        listed = list(response.context["markers"])

        assert listed[0] == old, "the highlighted marker should lead the list"
        assert newest in listed
        assert listed.index(old) < listed.index(newest)

    def test_ordering_falls_back_to_recency_within_the_same_flag(self):
        first = MarkerFactory()
        second = MarkerFactory()

        response = self.client.get(reverse("collection"))
        listed = list(response.context["markers"])

        assert listed.index(second) < listed.index(first)
