from django.urls import reverse
from rest_framework import status
from django.test import TestCase

from core.models import Object
from users.models import User

EXAMPLE_OBJECT_PATH = "src/users/tests/test_files/example_object.gif"
EXAMPLE_OBJECT_SIZE = 70122  # Size in bytes of the example object gif


class TestObjectUpload(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "testpassword"
        User.objects.create_user(
            username=self.username,
            password=self.password,
            is_staff=False,
            is_superuser=False,
        )

    def test_upload_object_unauthenticated(self):
        url = reverse("object-upload")
        with open(EXAMPLE_OBJECT_PATH, "rb") as image_file:
            data = {
                "source": image_file,
                "author": "Test Author",
                "title": "Test Marker",
                "scale": "1,1,1",  # Default scale
                "position": "0,0,0",  # Default position
                "rotation": "0,0,0",  # Default rotation
            }
            response = self.client.post(url, data)
        assert response.status_code == status.HTTP_302_FOUND  # Redirect to login page
        assert "/users/login" in response.url

    def test_upload_object_authenticated(self):
        url = reverse("object-upload")
        with open(EXAMPLE_OBJECT_PATH, "rb") as image_file:
            data = {
                "source": image_file,
                "author": "Test Author",
                "title": "Test Marker",
                "scale": "1,1,1",  # Default scale
                "position": "0,0,0",  # Default position
                "rotation": "0,0,0",  # Default rotation
            }

            self.client.login(username=self.username, password=self.password)
            response = self.client.post(url, data)
        assert response.status_code == status.HTTP_302_FOUND  # Redirect to home page

        # Verify that a Object instance was created
        assert Object.objects.count() == 1
        object = Object.objects.first()
        assert object.title == "Test Marker"
        assert object.author == "Test Author"
        assert object.file_size == EXAMPLE_OBJECT_SIZE
        assert object.source.name == "objects/example_object.gif"
        assert object.scale == "1,1,1"
        assert object.position == "0,0,0"
        assert object.rotation == "0,0,0"
