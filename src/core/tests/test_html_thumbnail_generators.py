from django.test import TestCase
from django.urls import reverse

from core.models import (
    DEFAULT_MARKER_THUMBNAIL_HEIGHT,
    DEFAULT_MARKER_THUMBNAIL_WIDTH,
    DEFAULT_OBJECT_THUMBNAIL_HEIGHT,
    DEFAULT_OBJECT_THUMBNAIL_WIDTH,
)
from core.tests.factory import (
    ArtworkFactory,
    ExhibitFactory,
    MarkerFactory,
    ObjectFactory,
)


class TestMarkerThumbnailGenerators(TestCase):
    def setUp(self):
        self.marker = MarkerFactory(
            title="Test Marker", source="markers/test.png", author="Test Author"
        )

    def test_marker_as_html(self):
        html = self.marker.as_html(height=100, width=200)
        assert 'height="100"' in html
        assert 'width="200"' in html
        assert f'id="{self.marker.id}"' in html
        assert f'title="{self.marker.title}"' in html
        assert self.marker.source.url in html
        assert "<img" in html

    def test_marker_thumbnail_not_editable(self):
        html = self.marker.as_html_thumbnail(editable=False)
        assert f'height="{DEFAULT_MARKER_THUMBNAIL_HEIGHT}"' in html
        assert f'width="{DEFAULT_MARKER_THUMBNAIL_WIDTH}"' in html
        assert reverse("edit-marker") not in html
        assert reverse("delete-content") not in html

    def test_marker_thumbnail_editable(self):
        html = self.marker.as_html_thumbnail(editable=True)

        edit_url = reverse("edit-marker", query={"id": self.marker.id})
        delete_url = reverse(
            "delete-content", query={"content_type": "marker", "id": self.marker.id}
        )

        assert f'href="{edit_url}"' in html
        assert f'href="{delete_url}"' in html

    def test_marker_in_use_cant_be_edited(self):
        # Create an artwork using this marker to mark it as "in use"
        ArtworkFactory(marker=self.marker)

        html = self.marker.as_html_thumbnail(editable=True)
        assert reverse("edit-marker") not in html
        assert reverse("delete-content") not in html


class TestObjectThumbnailGenerators(TestCase):
    def setUp(self):
        self.image_object = ObjectFactory(
            title="Test Image", source="objects/test.gif", scale="2 1", position="0 1 0"
        )
        self.video_object = ObjectFactory(
            title="Test Video", source="objects/test.mp4", scale="1 1", position="1 0 0"
        )

    def test_gif_object_as_html_is_image(self):
        html = self.image_object.as_html(height=100, width=200)
        assert 'height="100"' in html
        assert 'width="200"' in html
        assert f'id="{self.image_object.id}"' in html
        assert f'title="{self.image_object.title}"' in html
        assert self.image_object.source.url in html
        assert "<img" in html

    def test_video_object_as_html_is_video(self):
        html = self.video_object.as_html(height=100, width=200)
        assert 'height="100"' in html
        assert 'width="200"' in html
        assert f'id="{self.video_object.id}"' in html
        assert "autoplay" in html
        assert "loop" in html
        assert "muted" in html
        assert "<video" in html

    def test_object_thumbnail_follows_proportion(self):
        html = self.image_object.as_html_thumbnail(editable=False)
        expected_height = (
            DEFAULT_OBJECT_THUMBNAIL_HEIGHT * self.image_object.yproportion
        )
        expected_width = DEFAULT_OBJECT_THUMBNAIL_WIDTH * self.image_object.xproportion

        assert f'height="{expected_height}"' in html
        assert f'width="{expected_width}"' in html
        assert reverse("edit-object") not in html
        assert reverse("delete-content") not in html

    def test_object_thumbnail_can_be_edited(self):
        html = self.image_object.as_html_thumbnail(editable=True)

        edit_url = reverse("edit-object", query={"id": self.image_object.id})
        delete_url = reverse(
            "delete-content",
            query={"content_type": "object", "id": self.image_object.id},
        )

        assert f'href="{edit_url}"' in html
        assert f'href="{delete_url}"' in html

    def test_object_in_use_cant_be_edited(self):
        # Create an artwork using this object to mark it as "in use"
        ArtworkFactory(augmented=self.image_object)

        html = self.image_object.as_html_thumbnail(editable=True)
        assert reverse("edit-object") not in html
        assert reverse("delete-content") not in html


class TestArtworkThumbnailGenerators(TestCase):
    def setUp(self):
        self.marker = MarkerFactory(
            title="Test Marker", source="markers/test.png", author="Test Author"
        )
        self.object = ObjectFactory(
            title="Test Object", source="objects/test.gif", author="Test Author"
        )
        self.artwork = ArtworkFactory(
            title="Test Artwork", marker=self.marker, augmented=self.object
        )

    def test_artwork_thumbnail_not_editable(self):
        html = self.artwork.as_html_thumbnail(editable=False)

        # Should contain marker and object thumbnails
        assert self.marker.source.url in html
        assert self.object.source.url in html

        # Should not contain edit/delete buttons
        assert reverse("edit-artwork") not in html
        assert reverse("delete-content") not in html
        assert reverse("artwork-preview") not in html

    def test_artwork_thumbnail_editable(self):
        html = self.artwork.as_html_thumbnail(editable=True)

        # Should contain marker and object thumbnails
        assert self.marker.source.url in html
        assert self.object.source.url in html

        # Should contain edit/delete/preview buttons with correct URLs
        edit_url = reverse("edit-artwork", query={"id": self.artwork.id})
        delete_url = reverse(
            "delete-content", query={"content_type": "artwork", "id": self.artwork.id}
        )
        preview_url = reverse("artwork-preview", query={"id": self.artwork.id})

        assert f'href="{edit_url}"' in html
        assert f'href="{delete_url}"' in html
        assert f'href="{preview_url}"' in html

    def test_artwork_in_use_cant_be_edited(self):
        # Create an exhibit using this artwork to mark it as "in use"
        exhibit = ExhibitFactory()
        exhibit.artworks.add(self.artwork)

        html = self.artwork.as_html_thumbnail(editable=True)

        # Should not contain edit/delete/preview buttons
        assert reverse("edit-artwork") not in html
        assert reverse("delete-content") not in html
        assert reverse("artwork-preview") not in html


class TestExhibitThumbnailGenerators(TestCase):
    def setUp(self):
        self.exhibit = ExhibitFactory(name="Test Exhibit", slug="test-exhibit")
        # Add a couple artworks to test the count
        artwork1 = ArtworkFactory()
        artwork2 = ArtworkFactory()
        self.exhibit.artworks.add(artwork1, artwork2)

    def test_exhibit_thumbnail_not_editable(self):
        html = self.exhibit.as_html_thumbnail(editable=False)

        # Check basic exhibit information
        assert self.exhibit.name in html
        assert self.exhibit.owner.user.username in html
        assert self.exhibit.date in html
        assert f"{self.exhibit.artworks_count} " in html

        # Check links
        assert f'href="/{self.exhibit.slug}/"' in html
        assert 'class="gotoExb"' in html
        assert reverse("exhibit-detail", query={"id": self.exhibit.id}) in html

        # Should not contain edit/delete buttons
        assert reverse("edit-exhibit") not in html
        assert reverse("delete-content") not in html

    def test_exhibit_thumbnail_editable(self):
        html = self.exhibit.as_html_thumbnail(editable=True)

        # Should contain all basic information
        assert self.exhibit.name in html
        assert self.exhibit.owner.user.username in html
        assert self.exhibit.date in html
        assert f"{self.exhibit.artworks_count} " in html

        # Check links
        assert f'href="/{self.exhibit.slug}/"' in html
        assert reverse("exhibit-detail", query={"id": self.exhibit.id}) in html

        # Should contain edit/delete buttons with correct URLs
        edit_url = reverse("edit-exhibit", query={"id": self.exhibit.id})
        delete_url = reverse(
            "delete-content", query={"content_type": "exhibit", "id": self.exhibit.id}
        )

        assert f'href="{edit_url}"' in html
        assert f'href="{delete_url}"' in html
