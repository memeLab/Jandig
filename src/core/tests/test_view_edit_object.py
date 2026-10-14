from django.core.files.storage import default_storage
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from core.models import Object, ObjectExtensions
from src.core.tests.factory import ArtworkFactory, ObjectFactory
from src.core.tests.utils import get_example_object
from src.users.tests.factory import ProfileFactory, UserFactory
from users.models import Profile, User

EXAMPLE_OBJECT_PATH = "src/core/tests/test_files/example_object.gif"
EXAMPLE_OBJECT_SIZE = 70122  # Size in bytes of the example object gif
EXAMPLE_GLB_PATH = "collection/objects/werewolf.glb"
EXAMPLE_MP4_PATH = "collection/objects/belotur.mp4"


class TestObjectEdit(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "testpassword"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            is_staff=False,
            is_superuser=False,
        )
        self.profile = Profile.objects.get(user=self.user)

    def get_example_object1(self):
        return get_example_object("antipodas.gif")

    def get_example_object2(self):
        return get_example_object("temaki.gif")

    def test_edit_object_unauthenticated(self):
        """Test that an unauthenticated user cannot access the edit object page."""
        url = reverse("edit-object")
        response = self.client.get(url)
        assert response.status_code == status.HTTP_302_FOUND  # Redirect to login page
        assert "/users/login" in response.url

    def test_edit_object_authenticated(self):
        """Test that an authenticated user can access the edit object page."""
        self.client.login(username=self.username, password=self.password)
        obj = ObjectFactory(
            title="Test Image",
            source=self.get_example_object1(),
            owner=self.profile,
        )
        url = reverse("edit-object", query={"id": obj.id})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_edit_object_as_another_user(self):
        """Test that a user cannot edit an object they do not own."""
        obj = ObjectFactory(
            title="Test Image",
            source=self.get_example_object1(),
            owner=self.profile,
        )

        another_user = User.objects.create_user(
            username="anotheruser",
            password="anotherpassword",
            is_staff=False,
            is_superuser=False,
        )
        # Log in as another user should not allow access to edit the object
        self.client.login(username=another_user.username, password="anotherpassword")
        url = reverse("edit-object", query={"id": obj.id})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Log in as the original user should allow access to edit the object
        self.client.logout()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_edit_object_title(self):
        """Test that the object title can be edited."""
        self.client.login(username=self.username, password=self.password)

        obj = ObjectFactory(
            title="Old Title",
            source=self.get_example_object1(),
            owner=self.profile,
            author="Old Author",
        )
        url = reverse("edit-object", query={"id": obj.id})
        response = self.client.post(
            url,
            {
                "title": "New Title",
                "source": obj.source,
                "author": obj.author,
            },
        )
        assert (
            response.status_code == status.HTTP_302_FOUND
        )  # Redirect after successful edit
        obj.refresh_from_db()
        assert obj.title == "New Title"
        # Compare two files by size and content
        assert obj.source.size == self.get_example_object1().size
        assert obj.source.read() == self.get_example_object1().read()
        assert obj.author == "Old Author"
        assert obj.owner == self.profile

    def test_edit_object_author(self):
        """Test that the object author can be edited."""
        self.client.login(username=self.username, password=self.password)

        obj = ObjectFactory(
            title="Old Title",
            source=self.get_example_object1(),
            owner=self.profile,
            author="Old Author",
        )
        url = reverse("edit-object", query={"id": obj.id})
        response = self.client.post(
            url,
            {
                "title": obj.title,
                "source": obj.source,
                "author": "New Author",
            },
        )
        assert (
            response.status_code == status.HTTP_302_FOUND
        )  # Redirect after successful edit
        obj.refresh_from_db()
        assert obj.author == "New Author"
        assert obj.title == "Old Title"
        # Compare two files by size and content
        assert obj.source.size == self.get_example_object1().size
        assert obj.source.read() == self.get_example_object1().read()

        assert obj.owner == self.profile

    def test_edit_object_source(self):
        """Test that the object source can be edited."""
        self.client.login(username=self.username, password=self.password)

        obj = ObjectFactory(
            title="Old Title",
            source=self.get_example_object1(),
            owner=self.profile,
            author="Old Author",
        )
        url = reverse("edit-object", query={"id": obj.id})
        new_source = self.get_example_object2()
        response = self.client.post(
            url,
            {
                "title": obj.title,
                "source": new_source,
                "author": obj.author,
            },
        )
        assert response.status_code == status.HTTP_302_FOUND

    def test_edit_object_if_used_by_self(self):
        """Test that an object can be edited if it is used by the user."""
        self.client.login(username=self.username, password=self.password)
        # Create a base object that the user owns
        obj = ObjectFactory(
            title="Test Image",
            source=self.get_example_object1(),
            owner=self.profile,
        )
        # Simulate the object being used by the user
        _ = ArtworkFactory(
            title="Test Artwork",
            author=self.profile,
            augmented=obj,
        )

        url = reverse("edit-object", query={"id": obj.id})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

        # Update every field
        response = self.client.post(
            url,
            {
                "title": "new title",
                "source": self.get_example_object2(),
                "author": "new author",
            },
        )

        assert response.status_code == status.HTTP_302_FOUND
        obj.refresh_from_db()
        assert obj.title == "new title"
        assert obj.source.size == self.get_example_object2().size
        assert obj.source.read() == self.get_example_object2().read()
        assert obj.author == "new author"
        assert obj.owner == self.profile

    def test_cannot_edit_object_source_if_used_by_other(self):
        """Test that an object source file cannot be edited if it is used by another user."""
        obj = ObjectFactory(
            title="Test Image",
            source=self.get_example_object1(),
            owner=self.profile,
            author="Old Author",
        )

        # Simulate the object being used by another user
        another_user = UserFactory(username="anotheruser", password="anotherpassword")
        another_profile = ProfileFactory(user=another_user)
        another_user_artwork = ArtworkFactory(
            title="Test Artwork",
            author=another_profile,
            augmented=obj,
        )

        self.client.login(username=self.username, password=self.password)
        url = reverse("edit-object", query={"id": obj.id})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        response = self.client.post(
            url,
            {
                "title": obj.title,
                "source": self.get_example_object2(),
                "author": obj.author,
            },
        )
        assert response.status_code == status.HTTP_200_OK  # Cannot edit source if used
        obj.refresh_from_db()
        assert obj.source.size == self.get_example_object1().size
        assert obj.source.read() == self.get_example_object1().read()
        assert obj.title == "Test Image"
        assert obj.author == "Old Author"
        assert obj.owner == self.profile

        # After freeing the object, the user should be able to edit it
        another_user_artwork.delete()

        response = self.client.post(
            url,
            {
                "title": obj.title,
                "source": self.get_example_object2(),
                "author": obj.author,
            },
        )
        assert response.status_code == status.HTTP_302_FOUND
        obj.refresh_from_db()
        assert obj.source.size == self.get_example_object2().size
        assert obj.source.read() == self.get_example_object2().read()
        assert obj.title == "Test Image"
        assert obj.author == "Old Author"
        assert obj.owner == self.profile

    def test_can_edit_object_attributes_if_used_by_other(self):
        """Test that the object attributes can be edited if it is used by another user. Except the source file."""

        obj = ObjectFactory(
            title="Test Image",
            source=self.get_example_object1(),
            owner=self.profile,
        )

        # Simulate the object being used by another user
        another_user = UserFactory(username="anotheruser", password="anotherpassword")
        another_profile = ProfileFactory(user=another_user)
        _ = ArtworkFactory(
            title="Test Artwork",
            author=another_profile,
            augmented=obj,
        )

        self.client.login(username=self.username, password=self.password)
        url = reverse("edit-object", query={"id": obj.id})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

        response = self.client.post(
            url,
            {
                "title": "new title",
                "source": obj.source,
                "author": "new author",
            },
        )
        assert response.status_code == status.HTTP_302_FOUND
        obj.refresh_from_db()
        assert obj.title == "new title"
        assert obj.source.size == self.get_example_object1().size
        assert obj.source.read() == self.get_example_object1().read()
        assert obj.author == "new author"
        assert obj.owner == self.profile


class TestObjectEditCrossType(TestCase):
    """Test that editing an object from one type to another cleans up type-specific files."""

    def setUp(self):
        self.username = "testuser"
        self.password = "testpassword"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )
        self.profile = Profile.objects.get(user=self.user)
        self.client.login(username=self.username, password=self.password)

    def _files_in_folder(self, pk):
        """List all files in the object's storage folder."""
        try:
            _, files = default_storage.listdir(f"objects/{pk}")
        except Exception:
            files = []
        return set(files)

    def _upload_gif_with_spritesheet(self):
        """Upload a GIF object with spritesheet via the upload view."""
        import json

        from django.core.files.base import ContentFile

        from core.spritesheet_converter import gif_to_spritesheet

        with open(EXAMPLE_OBJECT_PATH, "rb") as f:
            gif_bytes = f.read()

        # Pre-generate spritesheet and metadata in storage (simulates HTMX step)
        png_bytes, metadata = gif_to_spritesheet(
            ContentFile(gif_bytes, name="test.gif")
        )

        spritesheet_path = default_storage.save(
            "objects/spritesheets/test_spritesheet.png", ContentFile(png_bytes)
        )
        metadata_path = default_storage.save(
            "objects/spritesheets/test_metadata.json",
            ContentFile(json.dumps(metadata).encode()),
        )

        with open(EXAMPLE_OBJECT_PATH, "rb") as f:
            response = self.client.post(
                reverse("object-upload"),
                {
                    "source": f,
                    "author": "Author",
                    "title": "GIF Object",
                    "spritesheet_path": spritesheet_path,
                    "spritesheet_metadata_path": metadata_path,
                },
            )
        assert response.status_code == status.HTTP_302_FOUND
        obj = Object.objects.get(title="GIF Object")
        assert obj.file_extension == ObjectExtensions.GIF
        assert obj.spritesheet_file
        assert obj.spritesheet_metadata
        return obj

    def _upload_glb_with_thumbnail(self):
        """Upload a GLB object with thumbnail via the upload view."""
        import io

        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image

        # Create a valid minimal PNG for thumbnail
        img = Image.new("RGBA", (4, 4), (255, 0, 0, 255))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        thumbnail = SimpleUploadedFile(
            "thumbnail.png", buf.getvalue(), content_type="image/png"
        )

        with open(EXAMPLE_GLB_PATH, "rb") as f:
            response = self.client.post(
                reverse("object-upload"),
                {
                    "source": f,
                    "author": "Author",
                    "title": "GLB Object",
                    "thumbnail": thumbnail,
                },
            )
        assert response.status_code == status.HTTP_302_FOUND
        obj = Object.objects.get(title="GLB Object")
        assert obj.file_extension == ObjectExtensions.GLB
        assert obj.thumbnail
        return obj

    def test_edit_gif_to_glb_cleans_spritesheet(self):
        """Editing a GIF object to GLB should remove spritesheet and metadata files."""
        obj = self._upload_gif_with_spritesheet()
        pk = obj.pk

        # Verify spritesheet files exist
        files_before = self._files_in_folder(pk)
        assert "spritesheet.png" in files_before
        assert "metadata.json" in files_before

        # Edit: change source to GLB (no spritesheet, no thumbnail)
        url = reverse("edit-object", query={"id": pk})
        with open(EXAMPLE_GLB_PATH, "rb") as f:
            response = self.client.post(
                url,
                {"source": f, "author": "Author", "title": "Now GLB"},
            )
        assert response.status_code == status.HTTP_302_FOUND
        obj.refresh_from_db()
        assert obj.file_extension == ObjectExtensions.GLB
        assert not obj.spritesheet_file
        assert not obj.spritesheet_metadata

        files_after = self._files_in_folder(pk)
        assert "spritesheet.png" not in files_after
        assert "metadata.json" not in files_after
        assert "source.glb" in files_after

    def test_edit_glb_to_gif_cleans_thumbnail(self):
        """Editing a GLB object to GIF should remove thumbnail file."""
        obj = self._upload_glb_with_thumbnail()
        pk = obj.pk

        # Verify thumbnail exists
        files_before = self._files_in_folder(pk)
        assert "thumbnail.png" in files_before

        # Edit: change source to GIF (no thumbnail)
        url = reverse("edit-object", query={"id": pk})
        with open(EXAMPLE_OBJECT_PATH, "rb") as f:
            response = self.client.post(
                url,
                {"source": f, "author": "Author", "title": "Now GIF"},
            )
        assert response.status_code == status.HTTP_302_FOUND
        obj.refresh_from_db()
        assert obj.file_extension == ObjectExtensions.GIF
        assert not obj.thumbnail

        files_after = self._files_in_folder(pk)
        assert "thumbnail.png" not in files_after
        assert "source.gif" in files_after

    def test_edit_gif_to_mp4_cleans_spritesheet(self):
        """Editing a GIF to MP4 should remove spritesheet files."""
        obj = self._upload_gif_with_spritesheet()
        pk = obj.pk

        url = reverse("edit-object", query={"id": pk})
        with open(EXAMPLE_MP4_PATH, "rb") as f:
            response = self.client.post(
                url,
                {"source": f, "author": "Author", "title": "Now MP4"},
            )
        assert response.status_code == status.HTTP_302_FOUND
        obj.refresh_from_db()
        assert obj.file_extension == ObjectExtensions.MP4
        assert not obj.spritesheet_file
        assert not obj.spritesheet_metadata

        files_after = self._files_in_folder(pk)
        assert "spritesheet.png" not in files_after
        assert "metadata.json" not in files_after
        assert "source.mp4" in files_after

    def test_edit_glb_to_gif_to_glb_cycle(self):
        """Full cycle: GLB(thumbnail) -> GIF(spritesheet) -> GLB(thumbnail)."""
        import io
        import json

        from django.core.files.base import ContentFile
        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image

        from core.spritesheet_converter import gif_to_spritesheet

        # Start with GLB+thumbnail
        obj = self._upload_glb_with_thumbnail()
        pk = obj.pk
        assert "thumbnail.png" in self._files_in_folder(pk)

        # Edit to GIF with spritesheet
        with open(EXAMPLE_OBJECT_PATH, "rb") as f:
            gif_bytes = f.read()
        png_bytes, metadata = gif_to_spritesheet(ContentFile(gif_bytes, name="t.gif"))
        spritesheet_path = default_storage.save(
            "objects/spritesheets/t_spritesheet.png", ContentFile(png_bytes)
        )
        metadata_path = default_storage.save(
            "objects/spritesheets/t_metadata.json",
            ContentFile(json.dumps(metadata).encode()),
        )

        url = reverse("edit-object", query={"id": pk})
        with open(EXAMPLE_OBJECT_PATH, "rb") as f:
            response = self.client.post(
                url,
                {
                    "source": f,
                    "author": "Author",
                    "title": "Now GIF",
                    "spritesheet_path": spritesheet_path,
                    "spritesheet_metadata_path": metadata_path,
                },
            )
        assert response.status_code == status.HTTP_302_FOUND
        obj.refresh_from_db()
        assert obj.file_extension == ObjectExtensions.GIF

        files_mid = self._files_in_folder(pk)
        assert "thumbnail.png" not in files_mid  # GLB thumbnail cleaned
        assert "spritesheet.png" in files_mid
        assert "metadata.json" in files_mid
        assert "source.gif" in files_mid

        # Edit back to GLB with thumbnail
        img = Image.new("RGBA", (4, 4), (0, 255, 0, 255))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        thumbnail = SimpleUploadedFile(
            "thumb.png", buf.getvalue(), content_type="image/png"
        )
        with open(EXAMPLE_GLB_PATH, "rb") as f:
            response = self.client.post(
                url,
                {
                    "source": f,
                    "author": "Author",
                    "title": "Back to GLB",
                    "thumbnail": thumbnail,
                },
            )
        assert response.status_code == status.HTTP_302_FOUND
        obj.refresh_from_db()
        assert obj.file_extension == ObjectExtensions.GLB

        files_final = self._files_in_folder(pk)
        assert "spritesheet.png" not in files_final  # GIF spritesheet cleaned
        assert "metadata.json" not in files_final  # GIF metadata cleaned
        assert "thumbnail.png" in files_final
        assert "source.glb" in files_final
