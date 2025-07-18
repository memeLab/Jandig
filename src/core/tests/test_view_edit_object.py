from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from src.core.tests.factory import ObjectFactory
from users.models import Profile, User

EXAMPLE_OBJECT_PATH = "src/users/tests/test_files/example_object.gif"
EXAMPLE_OBJECT_SIZE = 70122  # Size in bytes of the example object gif


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
            source="objects/test.gif",
            scale="2 1",
            position="0 1 0",
            owner=self.profile,
        )
        url = reverse("edit-object", query={"id": obj.id})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert "Edit Object" in response.content.decode()

    def test_edit_object_as_another_user(self):
        """Test that a user cannot edit an object they do not own."""
        obj = ObjectFactory(
            title="Test Image",
            source="objects/test.gif",
            scale="2 1",
            position="0 1 0",
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
