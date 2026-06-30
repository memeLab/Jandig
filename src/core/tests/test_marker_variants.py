from io import BytesIO

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.test import TestCase
from django.urls import reverse
from PIL import Image
from rest_framework import status

from core.marker_utils import generate_marker_variants
from core.models import Marker
from users.models import User


def create_test_image(width=100, height=100, color=(255, 0, 0), fmt="JPEG"):
    """Create a test image in memory."""
    image = Image.new("RGB", (width, height), color)
    blob = BytesIO()
    image.save(blob, fmt)
    blob.seek(0)
    return blob


class TestMarkerVariantGeneration(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "testpassword"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            is_staff=False,
            is_superuser=False,
        )
        self.profile = self.user.profile

    def _create_marker_with_source(self):
        """Helper to create a marker with a source image."""
        image_content = create_test_image()
        marker = Marker.objects.create(
            owner=self.profile,
            author="Test Author",
            title="Test Marker",
            source=ContentFile(image_content.read(), name="test_image.jpg"),
            patt=ContentFile(b"placeholder", name="test.patt"),
        )
        return marker

    def test_generate_variants_creates_all_files(self):
        """When a marker is processed, all 4 image files are generated and stored."""
        marker = self._create_marker_with_source()
        generate_marker_variants(marker)

        marker.refresh_from_db()

        # All fields should be populated
        assert marker.source.name == f"markers/{marker.pk}/original.jpg"
        assert marker.marker_img.name == f"markers/{marker.pk}/marker.png"
        assert marker.print_img.name == f"markers/{marker.pk}/print.png"
        assert marker.thumb_img.name == f"markers/{marker.pk}/thumb.png"
        assert marker.patt.name == f"markers/{marker.pk}/marker.patt"

        # Files should exist in storage
        assert default_storage.exists(marker.source.name)
        assert default_storage.exists(marker.marker_img.name)
        assert default_storage.exists(marker.print_img.name)
        assert default_storage.exists(marker.thumb_img.name)
        assert default_storage.exists(marker.patt.name)

    def test_generate_variants_marker_dimensions(self):
        """marker.png should be 256x256."""
        marker = self._create_marker_with_source()
        generate_marker_variants(marker)
        marker.refresh_from_db()

        with marker.marker_img.open("rb") as f:
            img = Image.open(f)
            assert img.size == (256, 256)

    def test_generate_variants_thumb_dimensions(self):
        """thumb.png should be 128x128."""
        marker = self._create_marker_with_source()
        generate_marker_variants(marker)
        marker.refresh_from_db()

        with marker.thumb_img.open("rb") as f:
            img = Image.open(f)
            assert img.size == (128, 128)

    def test_generate_variants_print_has_borders(self):
        """print.png should be larger than the original (has borders added)."""
        marker = self._create_marker_with_source()
        generate_marker_variants(marker)
        marker.refresh_from_db()

        with marker.source.open("rb") as f:
            original = Image.open(f)
            original_size = original.size

        with marker.print_img.open("rb") as f:
            print_img = Image.open(f)
            print_size = print_img.size

        # Print image should be larger due to borders
        assert print_size[0] > original_size[0]
        assert print_size[1] > original_size[1]

    def test_generate_variants_idempotent(self):
        """Re-running generate_marker_variants should overwrite existing files safely."""
        marker = self._create_marker_with_source()
        generate_marker_variants(marker)
        marker.refresh_from_db()

        first_marker_img_name = marker.marker_img.name

        # Run again
        generate_marker_variants(marker)
        marker.refresh_from_db()

        # Same paths (idempotent)
        assert marker.marker_img.name == first_marker_img_name
        assert default_storage.exists(marker.marker_img.name)

    def test_generate_variants_file_size_updated(self):
        """file_size should be updated to the print image size."""
        marker = self._create_marker_with_source()
        generate_marker_variants(marker)
        marker.refresh_from_db()

        assert marker.file_size > 0

    def test_generate_variants_patt_generated(self):
        """Patt file should be generated from the original image."""
        marker = self._create_marker_with_source()
        generate_marker_variants(marker)
        marker.refresh_from_db()

        with marker.patt.open("rb") as f:
            patt_content = f.read()

        # Patt files have a specific format (text-based with color values)
        assert len(patt_content) > 0
        # Should be text content (patt format)
        patt_text = patt_content.decode("utf-8")
        assert len(patt_text.strip()) > 0


class TestMarkerUploadWithVariants(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "testpassword"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            is_staff=False,
            is_superuser=False,
        )
        self.client.login(username=self.username, password=self.password)

    def test_upload_marker_generates_all_variants(self):
        """When a user uploads a new marker, all 4 image files are generated."""
        url = reverse("marker-upload")
        image_content = create_test_image()

        data = {
            "source": ContentFile(image_content.read(), name="upload_test.jpg"),
            "title": "Upload Test",
            "author": "Test Author",
        }
        response = self.client.post(url, data)
        assert response.status_code == status.HTTP_302_FOUND

        marker = Marker.objects.first()
        assert marker is not None

        # All variant files should exist
        assert marker.source.name == f"markers/{marker.pk}/original.jpg"
        assert marker.marker_img.name == f"markers/{marker.pk}/marker.png"
        assert marker.print_img.name == f"markers/{marker.pk}/print.png"
        assert marker.thumb_img.name == f"markers/{marker.pk}/thumb.png"

        assert default_storage.exists(marker.source.name)
        assert default_storage.exists(marker.marker_img.name)
        assert default_storage.exists(marker.print_img.name)
        assert default_storage.exists(marker.thumb_img.name)

    def test_edit_marker_regenerates_variants(self):
        """When a user edits a marker with a new image, all variants are regenerated."""
        # First create a marker
        url = reverse("marker-upload")
        image_content = create_test_image(color=(255, 0, 0))
        data = {
            "source": ContentFile(image_content.read(), name="original.jpg"),
            "title": "Edit Test",
            "author": "Test Author",
        }
        self.client.post(url, data)
        marker = Marker.objects.first()

        # Now edit with a new image
        edit_url = reverse("edit-marker") + f"?id={marker.pk}"
        new_image = create_test_image(color=(0, 255, 0))
        data = {
            "source": ContentFile(new_image.read(), name="new_image.jpg"),
            "title": "Edit Test Updated",
            "author": "Test Author",
        }
        response = self.client.post(edit_url, data)
        assert response.status_code == status.HTTP_302_FOUND

        marker.refresh_from_db()

        # Variants should still exist at the same paths (overwritten)
        assert marker.marker_img.name == f"markers/{marker.pk}/marker.png"
        assert default_storage.exists(marker.marker_img.name)
        assert default_storage.exists(marker.print_img.name)
        assert default_storage.exists(marker.thumb_img.name)


class TestMarkerDeletion(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "testpassword"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            is_staff=False,
            is_superuser=False,
        )
        self.profile = self.user.profile
        self.client.login(username=self.username, password=self.password)

    def test_delete_marker_removes_all_files(self):
        """When a user deletes a marker, all files are removed from storage."""
        # Create marker with variants
        image_content = create_test_image()
        marker = Marker.objects.create(
            owner=self.profile,
            author="Test Author",
            title="Delete Test",
            source=ContentFile(image_content.read(), name="delete_test.jpg"),
            patt=ContentFile(b"placeholder", name="test.patt"),
        )
        generate_marker_variants(marker)
        marker.refresh_from_db()

        # Store paths before deletion
        source_path = marker.source.name
        marker_img_path = marker.marker_img.name
        print_img_path = marker.print_img.name
        thumb_img_path = marker.thumb_img.name
        patt_path = marker.patt.name

        # Verify files exist before deletion
        assert default_storage.exists(source_path)
        assert default_storage.exists(marker_img_path)
        assert default_storage.exists(print_img_path)
        assert default_storage.exists(thumb_img_path)
        assert default_storage.exists(patt_path)

        # Delete via the view
        delete_url = reverse("delete-content") + f"?content_type=marker&id={marker.pk}"
        self.client.get(delete_url)

        # Marker should be deleted from DB
        assert Marker.objects.count() == 0

        # All files should be removed from storage
        assert not default_storage.exists(source_path)
        assert not default_storage.exists(marker_img_path)
        assert not default_storage.exists(print_img_path)
        assert not default_storage.exists(thumb_img_path)
        assert not default_storage.exists(patt_path)

    def test_delete_marker_via_model(self):
        """Direct model deletion also removes all files."""
        image_content = create_test_image()
        marker = Marker.objects.create(
            owner=self.profile,
            author="Test Author",
            title="Model Delete Test",
            source=ContentFile(image_content.read(), name="model_delete.jpg"),
            patt=ContentFile(b"placeholder", name="test.patt"),
        )
        generate_marker_variants(marker)
        marker.refresh_from_db()

        source_path = marker.source.name
        marker_img_path = marker.marker_img.name

        marker.delete()

        assert not default_storage.exists(source_path)
        assert not default_storage.exists(marker_img_path)
