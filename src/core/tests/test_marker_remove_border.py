import io

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image
from pymarker import generate_marker_from_image

from core.models import Marker
from users.models import User

PLAIN_SIZE = (200, 200)


def already_a_marker():
    """An upload that already carries a marker border, as users often send."""
    plain = Image.new("RGB", PLAIN_SIZE, "white")
    bordered = generate_marker_from_image(
        plain,
        black_border_percentage=20,
        white_border_percentage=3,
        inner_border_percentage=0,
    )
    buffer = io.BytesIO()
    bordered.save(buffer, format="PNG")
    buffer.seek(0)
    return SimpleUploadedFile("bordered.png", buffer.read(), content_type="image/png")


def stored_size(marker):
    with Image.open(marker.source) as image:
        return image.size


class TestRemoveExistingBorder(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "testpassword"
        User.objects.create_user(username=self.username, password=self.password)
        self.client.login(username=self.username, password=self.password)

    def upload(self, title, **extra):
        return self.client.post(
            reverse("marker-upload"),
            {
                "source": already_a_marker(),
                "title": title,
                "author": "Test Author",
                **extra,
            },
        )

    def test_the_upload_really_arrives_with_a_border(self):
        """Guards the fixture: without this the other tests prove nothing."""
        self.upload("as uploaded")
        marker = Marker.objects.get(title="as uploaded")

        assert stored_size(marker) > PLAIN_SIZE

    def test_ticking_the_box_strips_the_existing_border(self):
        self.upload("stripped", remove_existing_border="on")
        marker = Marker.objects.get(title="stripped")

        assert stored_size(marker) == PLAIN_SIZE

    def test_leaving_the_box_unticked_keeps_the_image_as_sent(self):
        self.upload("kept")
        marker = Marker.objects.get(title="kept")

        assert stored_size(marker) != PLAIN_SIZE

    def test_stripping_avoids_the_recursive_border(self):
        """
        Generating a marker from an already-bordered image nests one border
        inside another, which is what the issue's screenshot shows.
        """
        self.upload("stripped", remove_existing_border="on")
        self.upload("kept")

        stripped = stored_size(Marker.objects.get(title="stripped"))
        kept = stored_size(Marker.objects.get(title="kept"))

        assert stripped[0] < kept[0]

    def test_the_form_still_works_together_with_the_inner_border_option(self):
        response = self.upload("both", remove_existing_border="on", inner_border="on")

        assert response.status_code == 302
        assert stored_size(Marker.objects.get(title="both")) == PLAIN_SIZE


class TestRemoveExistingBorderOnEdit(TestCase):
    """Editing goes through UploadMarkerForm.save(), not the upload view."""

    def setUp(self):
        self.username = "testuser"
        self.password = "testpassword"
        user = User.objects.create_user(username=self.username, password=self.password)
        self.client.login(username=self.username, password=self.password)
        self.client.post(
            reverse("marker-upload"),
            {"source": already_a_marker(), "title": "original", "author": "A"},
        )
        self.marker = Marker.objects.get(title="original")
        assert self.marker.owner == user.profile

    def test_editing_with_the_box_ticked_strips_the_border(self):
        response = self.client.post(
            f"{reverse('edit-marker')}?id={self.marker.pk}",
            {
                "source": already_a_marker(),
                "title": "original",
                "author": "A",
                "remove_existing_border": "on",
            },
        )

        assert response.status_code == 302
        self.marker.refresh_from_db()
        assert stored_size(self.marker) == PLAIN_SIZE
