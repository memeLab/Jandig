from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from core.models import Object, ObjectExtensions
from users.models import Profile, User

EXAMPLE_OBJECT_PATH = "src/core/tests/test_files/example_object.gif"
EXAMPLE_MP4_OBJECT_PATH = "collection/objects/belotur.mp4"
EXAMPLE_WEBM_OBJECT_PATH = "collection/objects/escher.webm"
EXAMPLE_GLB_OBJECT_PATH = "collection/objects/werewolf.glb"


class TestObjectUpload(TestCase):
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

    def test_upload_object_unauthenticated(self):
        url = reverse("object-upload")
        with open(EXAMPLE_OBJECT_PATH, "rb") as image_file:
            data = {
                "source": image_file,
                "author": "Test Author",
                "title": "Test Marker",
            }
            response = self.client.post(url, data)
        assert response.status_code == status.HTTP_302_FOUND  # Redirect to login page
        assert "/users/login" in response.url

    def test_upload_object_gif_authenticated(self):
        with open(EXAMPLE_OBJECT_PATH, "rb") as image_file:
            data = {
                "source": image_file,
                "author": "Test Author",
                "title": "Test Marker",
            }

            self.client.login(username=self.username, password=self.password)
            response = self.client.post(reverse("object-upload"), data)
            assert (
                response.status_code == status.HTTP_302_FOUND
            )  # Redirect to home page

        # Verify that a Object instance was created
        assert Object.objects.count() == 1
        ar_object = Object.objects.first()
        assert ar_object.title == "Test Marker"
        assert ar_object.author == "Test Author"
        assert ar_object.file_size == 70122  # Size in bytes of the example object gif

        assert ar_object.file_name_original == "example_object.gif"
        assert ar_object.file_extension == ObjectExtensions.GIF

    def test_upload_object_mp4_authenticated(self):
        with open(EXAMPLE_MP4_OBJECT_PATH, "rb") as video_file:
            data = {
                "source": video_file,
                "author": "Test Author",
                "title": "Test Video",
            }

            self.client.login(username=self.username, password=self.password)
            response = self.client.post(reverse("object-upload"), data)
            assert (
                response.status_code == status.HTTP_302_FOUND
            )  # Redirect to home page
        # Verify that a Object instance was created
        assert Object.objects.count() == 1
        ar_object = Object.objects.first()
        assert ar_object.title == "Test Video"
        assert ar_object.author == "Test Author"
        assert ar_object.file_size == 2222838  # Size in bytes of the example mp4
        assert ar_object.file_name_original == "belotur.mp4"
        assert ar_object.file_extension == ObjectExtensions.MP4

    def test_upload_object_webm_authenticated(self):
        with open(EXAMPLE_WEBM_OBJECT_PATH, "rb") as video_file:
            data = {
                "source": video_file,
                "author": "Test Author",
                "title": "Test Video",
            }

            self.client.login(username=self.username, password=self.password)
            response = self.client.post(reverse("object-upload"), data)
            assert (
                response.status_code == status.HTTP_302_FOUND
            )  # Redirect to home page
        # Verify that a Object instance was created
        assert Object.objects.count() == 1
        ar_object = Object.objects.first()
        assert ar_object.title == "Test Video"
        assert ar_object.author == "Test Author"
        assert ar_object.file_size == 1509266  # Size in bytes of the example webm
        assert ar_object.file_name_original == "escher.webm"
        assert ar_object.file_extension == ObjectExtensions.WEBM

    def test_upload_object_glb_authenticated(self):
        with open(EXAMPLE_GLB_OBJECT_PATH, "rb") as glb_file:
            data = {
                "source": glb_file,
                "author": "Test Author",
                "title": "Test GLB",
            }

            self.client.login(username=self.username, password=self.password)
            response = self.client.post(reverse("object-upload"), data)
            assert (
                response.status_code == status.HTTP_302_FOUND
            )  # Redirect to home page
        # Verify that a Object instance was created
        assert Object.objects.count() == 1
        ar_object = Object.objects.first()
        assert ar_object.title == "Test GLB"
        assert ar_object.author == "Test Author"
        assert ar_object.file_size == 10782148  # Size in bytes of the example glb
        assert ar_object.file_name_original == "werewolf.glb"
        assert ar_object.file_extension == ObjectExtensions.GLB

    def test_upload_object_get_authenticated(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse("object-upload"))
        assert response.status_code == 200
        assert b"Object's title" in response.content  # Form is rendered

    def test_upload_object_post_invalid_missing_fields(self):
        self.client.login(username=self.username, password=self.password)
        data = {
            "author": "Test Author",
            "title": "Test Marker",
            # Missing 'source'
        }
        response = self.client.post(reverse("object-upload"), data)
        assert response.status_code == 200
        assert b"This field is required" in response.content
        assert Object.objects.count() == 0

        data = {
            "source": SimpleUploadedFile("test.gif", b"test content"),
            # missing 'title'
            "author": "Test Author",
        }

        response = self.client.post(reverse("object-upload"), data)
        assert response.status_code == 200
        assert b"This field is required" in response.content
        assert Object.objects.count() == 0

    def test_upload_object_post_invalid_file_type(self):
        self.client.login(username=self.username, password=self.password)
        fake_file = SimpleUploadedFile(
            "test.txt", b"not an image", content_type="text/plain"
        )
        data = {
            "source": fake_file,
            "author": "Test Author",
            "title": "Test Marker",
        }
        response = self.client.post(reverse("object-upload"), data)
        # Should fail validation or be rejected by the form
        assert response.status_code == 200
        assert (
            b"Only GIF images, MP4, WebM videos, and GLB files are allowed."
            in response.content
        )
        assert Object.objects.count() == 0

    def test_upload_object_permission_denied_for_anonymous(self):
        response = self.client.get(reverse("object-upload"))
        assert response.status_code == status.HTTP_302_FOUND
        assert "/users/login" in response.url
