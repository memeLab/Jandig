from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from core.models import Object
from users.models import Profile, User

EXAMPLE_OBJECT_PATH = "src/users/tests/test_files/example_object.gif"
EXAMPLE_OBJECT_SIZE = 70122  # Size in bytes of the example object gif


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
                "scale": "1",  # Default scale
                "position": "0,0,0",  # Default position
                "rotation": "270,0,0",  # Default rotation
            }
            response = self.client.post(url, data)
        assert response.status_code == status.HTTP_302_FOUND  # Redirect to login page
        assert "/users/login" in response.url

    def test_upload_object_authenticated(self):
        with open(EXAMPLE_OBJECT_PATH, "rb") as image_file:
            data = {
                "source": image_file,
                "author": "Test Author",
                "title": "Test Marker",
                "scale": "3",
                "position": "0 0 0",  # Default position
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
        assert ar_object.file_size == EXAMPLE_OBJECT_SIZE
        assert ar_object.source.name == "objects/example_object.gif"

        assert ar_object.scale == "3.00 3.00"
        assert ar_object.position == "0 0 0"
        assert ar_object.rotation == "270 0 0"

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
            "scale": "1",
            "position": "0,0,0",
        }
        response = self.client.post(reverse("object-upload"), data)
        assert response.status_code == 200
        assert b"This field is required" in response.content
        assert Object.objects.count() == 0

        data = {
            "source": SimpleUploadedFile("test.gif", b"test content"),
            # missing 'title'
            "author": "Test Author",
            "scale": "1",
            "position": "0,0,0",
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
            "scale": "1",
            "position": "0,0,0",
        }
        response = self.client.post(reverse("object-upload"), data)
        # Should fail validation or be rejected by the form
        assert response.status_code == 200
        assert (
            b"Only GIF images, MP4, WebM videos, and GLB files are allowed."
            in response.content
        )
        assert Object.objects.count() == 0

    def test_upload_object_post_invalid_scale(self):
        self.client.login(username=self.username, password=self.password)
        with open(EXAMPLE_OBJECT_PATH, "rb") as image_file:
            data = {
                "source": image_file,
                "author": "Test Author",
                "title": "Test Marker",
                "scale": "10",  # Invalid scale
                "position": "0,0,0",
            }
            response = self.client.post(reverse("object-upload"), data)
            assert response.status_code == 200
            print(response.content)
            # Note: No idea where this message is from, probably from the max_value in the form
            assert b"Ensure this value is less than or equal to 5.0" in response.content
            assert Object.objects.count() == 0

            data["scale"] = "0"  # Invalid scale
            response = self.client.post(reverse("object-upload"), data)
            assert response.status_code == 200
            assert (
                b"Ensure this value is greater than or equal to 0.1" in response.content
            )
            assert Object.objects.count() == 0

    def test_upload_object_permission_denied_for_anonymous(self):
        response = self.client.get(reverse("object-upload"))
        assert response.status_code == status.HTTP_302_FOUND
        assert "/users/login" in response.url
