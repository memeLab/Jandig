"""Guard the ordering of the <slug:slug> detail routes.

They were originally inserted alphabetically, which put them *before* their
literal siblings. Django matches in order and "upload", "edit", "create" and
"convert-spritesheet" all satisfy the slug converter, so every POST to those
endpoints resolved to a GET-only detail view and came back 405.
"""

from django.test import TestCase
from django.urls import resolve, reverse

# Each literal route that a sibling <slug:slug> pattern could swallow.
LITERAL_ROUTES = [
    ("create-artwork", "create_artwork"),
    ("edit-artwork", "edit_artwork"),
    ("edit-marker", "edit_marker"),
    ("marker-upload", "marker_upload"),
    ("edit-object", "edit_object"),
    ("object-upload", "object_upload"),
    ("convert-spritesheet", "convert_gif_to_spritesheet"),
]

DETAIL_VIEWS = {"artwork_detail", "marker_detail", "object_detail"}


class TestUrlResolutionOrder(TestCase):
    def test_literal_routes_are_not_swallowed_by_a_slug_pattern(self):
        for route_name, expected_view in LITERAL_ROUTES:
            with self.subTest(route=route_name):
                match = resolve(reverse(route_name))
                assert match.func.__name__ == expected_view, (
                    f"{route_name} resolved to {match.func.__name__}; a "
                    "<slug:slug> pattern is matching before it"
                )
                assert match.func.__name__ not in DETAIL_VIEWS

    def test_the_slug_routes_still_resolve_for_a_real_slug(self):
        for route_name, expected_view in [
            ("artwork-detail", "artwork_detail"),
            ("marker-detail", "marker_detail"),
            ("object-detail", "object_detail"),
        ]:
            with self.subTest(route=route_name):
                url = reverse(route_name, kwargs={"slug": "some-real-slug"})
                assert resolve(url).func.__name__ == expected_view
