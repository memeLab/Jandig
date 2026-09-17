import io
from unittest import mock

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from core.models import Marker
from users.models import User


def upload_file(name="Minha imagem #1.png"):
    buffer = io.BytesIO()
    Image.new("RGB", (120, 120), "white").save(buffer, format="PNG")
    buffer.seek(0)
    return SimpleUploadedFile(name, buffer.read(), content_type="image/png")


class TestMarkerCleanupLogging(TestCase):
    """A failed cleanup leaves a user-named file public; it must be loud."""

    def setUp(self):
        self.username = "testuser"
        self.password = "testpassword"
        User.objects.create_user(username=self.username, password=self.password)
        self.client.login(username=self.username, password=self.password)

    def upload(self, title="Marker"):
        return self.client.post(
            reverse("marker-upload"),
            {"source": upload_file(), "title": title, "author": "Test Author"},
        )

    def test_the_uploaded_file_is_renamed_away_from_the_users_filename(self):
        self.upload("renamed")
        marker = Marker.objects.get(title="renamed")

        assert marker.source.name == f"markers/{marker.pk}/original.png"
        assert "Minha imagem" not in marker.source.name

    def test_a_failed_cleanup_is_logged_with_the_path_left_behind(self):
        # Patch the storage instance the FileField actually uses, rather than a
        # storage class: the test settings swap in an in-memory backend.
        with mock.patch.object(
            default_storage, "delete", side_effect=OSError("storage refused")
        ):
            with self.assertLogs("core.marker_utils", level="ERROR") as logs:
                response = self.upload("cleanup failed")

        assert response.status_code == 302, "the upload itself must still succeed"
        assert Marker.objects.filter(title="cleanup failed").exists()
        logged = "\n".join(logs.output)
        # Django's get_valid_name sanitises the name but does not anonymise it:
        # "Minha imagem #1.png" reaches storage as "Minha_imagem_1.png", still
        # recognisably the uploader's, which is the whole point of #989.
        assert "Minha_imagem" in logged, (
            "the log must name the file still sitting in storage"
        )
        assert "storage refused" in logged, "the original exception must be included"

    def test_a_successful_cleanup_logs_nothing(self):
        with mock.patch("core.marker_utils.log") as logger:
            self.upload("clean")

        logger.exception.assert_not_called()
