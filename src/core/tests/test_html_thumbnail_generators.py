from django.template import engines
from django.test import TestCase
from django.urls import reverse

from core.models import (
    ExhibitTypes,
)
from core.tests.factory import (
    ArtworkFactory,
    ExhibitFactory,
    MarkerFactory,
    ObjectFactory,
)
from core.tests.utils import get_example_object


def render_template(template_name, context):
    """Render a Jinja2 template with the given context."""
    jinja_engine = engines["jinja2"]
    template = jinja_engine.get_template(template_name)
    return template.render(context)


class TestMarkerThumbnailTemplates(TestCase):
    def setUp(self):
        self.marker = MarkerFactory(title="Test Marker", author="Test Author")

    def test_marker_as_html(self):
        html = self.marker.as_html(height=100, width=200)
        assert 'height="100"' in html
        assert 'width="200"' in html
        assert f'id="{self.marker.id}"' in html
        assert f'title="{self.marker.title}"' in html
        assert self.marker.print_img.url in html
        assert "<img" in html

    def test_marker_thumbnail_not_editable(self):
        html = render_template(
            "core/templates/marker_thumbnail.jinja2",
            {"marker": self.marker, "editable": False},
        )
        assert self.marker.thumb_img.url in html
        assert "action-menu-container" not in html

    def test_marker_thumbnail_editable(self):
        html = render_template(
            "core/templates/marker_thumbnail.jinja2",
            {"marker": self.marker, "editable": True},
        )
        assert "action-menu-container" in html
        edit_url = reverse("edit-marker") + f"?id={self.marker.id}"
        preview_url = reverse("marker-preview") + f"?id={self.marker.id}"
        delete_url = (
            reverse("delete-content") + f"?content_type=marker&amp;id={self.marker.id}"
        )
        assert edit_url in html
        assert delete_url in html
        assert preview_url in html

    def test_marker_in_use_shows_disabled_actions(self):
        ArtworkFactory(marker=self.marker)
        html = render_template(
            "core/templates/marker_thumbnail.jinja2",
            {"marker": self.marker, "editable": True},
        )
        # Menu should still be present
        assert "action-menu-container" in html
        # Delete should be disabled (data-disabled attribute present)
        assert 'data-disabled="true"' in html


class TestObjectThumbnailTemplates(TestCase):
    def setUp(self):
        self.image_object = ObjectFactory(
            title="Test Image",
            source=get_example_object("peixe.gif"),
        )
        self.video_object = ObjectFactory(
            title="Test Video",
            source=get_example_object("belotur.mp4"),
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

    def test_object_thumbnail_editable(self):
        html = render_template(
            "core/templates/object_thumbnail.jinja2",
            {"object": self.image_object, "editable": True},
        )
        assert "action-menu-container" in html
        edit_url = reverse("edit-object") + f"?id={self.image_object.id}"
        delete_url = (
            reverse("delete-content")
            + f"?content_type=object&amp;id={self.image_object.id}"
        )
        assert edit_url in html
        assert delete_url in html

    def test_object_in_use_by_others_shows_disabled(self):
        ArtworkFactory(augmented=self.image_object)
        html = render_template(
            "core/templates/object_thumbnail.jinja2",
            {"object": self.image_object, "editable": True},
        )
        assert "action-menu-container" in html
        assert 'data-disabled="true"' in html

    def test_object_in_use_by_self_can_be_edited(self):
        ArtworkFactory(augmented=self.image_object, author=self.image_object.owner)
        html = render_template(
            "core/templates/object_thumbnail.jinja2",
            {"object": self.image_object, "editable": True},
        )
        edit_url = reverse("edit-object") + f"?id={self.image_object.id}"
        # In use only by self, so edit should be a real link (no data-disabled)
        assert f'href="{edit_url}"' in html


class TestArtworkThumbnailTemplates(TestCase):
    def setUp(self):
        self.marker = MarkerFactory(title="Test Marker", author="Test Author")
        self.object = ObjectFactory(
            title="Test Object",
            source=get_example_object("peixe.gif"),
            author="Test Author",
        )
        self.artwork = ArtworkFactory(
            title="Test Artwork", marker=self.marker, augmented=self.object
        )

    def test_artwork_thumbnail_not_editable(self):
        html = render_template(
            "core/templates/artwork_thumbnail.jinja2",
            {"artwork": self.artwork, "editable": False},
        )
        assert self.marker.thumb_img.url in html
        assert self.object.source.url in html
        assert "action-menu-container" not in html

    def test_artwork_thumbnail_editable(self):
        html = render_template(
            "core/templates/artwork_thumbnail.jinja2",
            {"artwork": self.artwork, "editable": True},
        )
        assert self.marker.thumb_img.url in html
        assert self.object.source.url in html
        assert "action-menu-container" in html
        edit_url = reverse("edit-artwork") + f"?id={self.artwork.id}"
        preview_url = reverse("artwork-preview") + f"?id={self.artwork.id}"
        delete_url = (
            reverse("delete-content")
            + f"?content_type=artwork&amp;id={self.artwork.id}"
        )
        assert edit_url in html
        assert delete_url in html
        assert preview_url in html

    def test_artwork_in_use_hides_delete(self):
        exhibit = ExhibitFactory()
        exhibit.artworks.add(self.artwork)
        html = render_template(
            "core/templates/artwork_thumbnail.jinja2",
            {"artwork": self.artwork, "editable": True},
        )
        # Edit should still work
        edit_url = reverse("edit-artwork") + f"?id={self.artwork.id}"
        assert f'href="{edit_url}"' in html
        # Delete should be disabled
        assert 'data-disabled="true"' in html


class TestExhibitThumbnailTemplates(TestCase):
    def setUp(self):
        self.exhibit = ExhibitFactory(name="Test Exhibit", slug="test-exhibit")
        artwork1 = ArtworkFactory()
        artwork2 = ArtworkFactory()
        self.exhibit.artworks.add(artwork1, artwork2)

    def test_exhibit_thumbnail_not_editable(self):
        html = render_template(
            "core/templates/exhibit_thumbnail.jinja2",
            {"exhibit": self.exhibit, "editable": False},
        )
        assert self.exhibit.name in html
        assert self.exhibit.owner.user.username in html
        assert self.exhibit.date in html
        assert f'href="/{self.exhibit.slug}/"' in html
        assert "action-menu-container" not in html

    def test_ar_exhibit_thumbnail_editable(self):
        self.exhibit.exhibit_type = ExhibitTypes.AR
        html = render_template(
            "core/templates/exhibit_thumbnail.jinja2",
            {"exhibit": self.exhibit, "editable": True},
        )
        assert self.exhibit.name in html
        assert self.exhibit.owner.user.username in html
        assert "action-menu-container" in html
        edit_url = reverse("edit-ar-exhibit") + f"?id={self.exhibit.id}"
        delete_url = (
            reverse("delete-content")
            + f"?content_type=ar-exhibit&amp;id={self.exhibit.id}"
        )
        assert edit_url in html
        assert delete_url in html

    def test_mr_exhibit_thumbnail_editable(self):
        self.exhibit.exhibit_type = ExhibitTypes.MR
        html = render_template(
            "core/templates/exhibit_thumbnail.jinja2",
            {"exhibit": self.exhibit, "editable": True},
        )
        assert self.exhibit.name in html
        assert "action-menu-container" in html
        edit_url = reverse("edit-mr-exhibit") + f"?id={self.exhibit.id}"
        delete_url = (
            reverse("delete-content")
            + f"?content_type=mr-exhibit&amp;id={self.exhibit.id}"
        )
        assert edit_url in html
        assert delete_url in html
