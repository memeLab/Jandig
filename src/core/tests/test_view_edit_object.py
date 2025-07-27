from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from src.core.tests.factory import ArtworkFactory, ObjectFactory
from src.core.tests.utils import get_example_object
from src.users.tests.factory import ProfileFactory, UserFactory
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
            scale="2 1",
            position="0 1 0",
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

    def test_edit_object_title(self):
        """Test that the object title can be edited."""
        self.client.login(username=self.username, password=self.password)

        obj = ObjectFactory(
            title="Old Title",
            source=self.get_example_object1(),
            scale="2.00 2.00",
            position="0 1 0",
            owner=self.profile,
            author="Old Author",
        )
        url = reverse("edit-object", query={"id": obj.id})
        response = self.client.post(
            url,
            {
                "title": "New Title",
                "source": obj.source,
                "scale": obj.scale.split(" ")[0],
                "position": obj.position,
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
        assert obj.scale == "2.00 2.00"
        assert obj.position == "0 1 0"
        assert obj.author == "Old Author"
        assert obj.owner == self.profile

    def test_edit_object_author(self):
        """Test that the object author can be edited."""
        self.client.login(username=self.username, password=self.password)

        obj = ObjectFactory(
            title="Old Title",
            source=self.get_example_object1(),
            scale="2.00 2.00",
            position="0 1 0",
            owner=self.profile,
            author="Old Author",
        )
        url = reverse("edit-object", query={"id": obj.id})
        response = self.client.post(
            url,
            {
                "title": obj.title,
                "source": obj.source,
                "scale": obj.scale.split(" ")[0],
                "position": obj.position,
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

        assert obj.scale == "2.00 2.00"
        assert obj.position == "0 1 0"
        assert obj.owner == self.profile

    def test_edit_object_source(self):
        """Test that the object source can be edited."""
        self.client.login(username=self.username, password=self.password)

        obj = ObjectFactory(
            title="Old Title",
            source=self.get_example_object1(),
            scale="2.00 2.00",
            position="0 1 0",
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
                "scale": obj.scale.split(" ")[0],
                "position": obj.position,
                "author": obj.author,
            },
        )
        assert response.status_code == status.HTTP_302_FOUND

    def test_edit_object_scale(self):
        """Test that the object scale can be edited."""
        self.client.login(username=self.username, password=self.password)

        obj = ObjectFactory(
            title="Old Title",
            source=self.get_example_object1(),
            scale="2.00 2.00",
            position="0 1 0",
            owner=self.profile,
            author="Old Author",
        )
        url = reverse("edit-object", query={"id": obj.id})
        response = self.client.post(
            url,
            {
                "title": obj.title,
                "source": obj.source,
                "scale": "3.00",
                "position": obj.position,
                "author": obj.author,
            },
        )
        assert (
            response.status_code == status.HTTP_302_FOUND
        )  # Redirect after successful edit
        obj.refresh_from_db()
        assert obj.scale == "3.00 3.00"
        assert obj.title == "Old Title"
        # Compare two files by size and content
        assert obj.source.size == self.get_example_object1().size
        assert obj.source.read() == self.get_example_object1().read()
        assert obj.position == "0 1 0"
        assert obj.author == "Old Author"
        assert obj.owner == self.profile

    def test_edit_object_position(self):
        """Test that the object position can be edited."""
        self.client.login(username=self.username, password=self.password)

        obj = ObjectFactory(
            title="Old Title",
            source=self.get_example_object1(),
            scale="2.00 2.00",
            position="0 1 0",
            owner=self.profile,
            author="Old Author",
        )
        url = reverse("edit-object", query={"id": obj.id})
        response = self.client.post(
            url,
            {
                "title": obj.title,
                "source": obj.source,
                "scale": obj.scale.split(" ")[0],
                "position": "1 2 3",
                "author": obj.author,
            },
        )
        assert response.status_code == status.HTTP_302_FOUND
        obj.refresh_from_db()
        assert obj.position == "1 2 3"
        assert obj.title == "Old Title"
        # Compare two files by size and content
        assert obj.source.size == self.get_example_object1().size
        assert obj.source.read() == self.get_example_object1().read()
        assert obj.scale == "2.00 2.00"
        assert obj.author == "Old Author"
        assert obj.owner == self.profile

    def test_edit_object_if_used_by_self(self):
        """Test that an object can be edited if it is used by the user."""
        self.client.login(username=self.username, password=self.password)
        # Create a base object that the user owns
        obj = ObjectFactory(
            title="Test Image",
            source=self.get_example_object1(),
            scale="2 1",
            position="0 1 0",
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
                "scale": "3.0",
                "position": "3 2 1",
                "author": "new author",
            },
        )

        assert response.status_code == status.HTTP_302_FOUND
        obj.refresh_from_db()
        assert obj.title == "new title"
        assert obj.source.size == self.get_example_object2().size
        assert obj.source.read() == self.get_example_object2().read()
        assert obj.scale == "3.00 3.00"
        assert obj.position == "3 2 1"
        assert obj.author == "new author"
        assert obj.owner == self.profile

    def test_cannot_edit_object_source_if_used_by_other(self):
        """Test that an object source file cannot be edited if it is used by another user."""
        obj = ObjectFactory(
            title="Test Image",
            source=self.get_example_object1(),
            scale="2.00 2.00",
            position="0 1 0",
            owner=self.profile,
            author="Old Author",
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
                "title": obj.title,
                "source": self.get_example_object2(),
                "scale": obj.scale.split(" ")[0],
                "position": obj.position,
                "author": obj.author,
            },
        )
        assert response.status_code == status.HTTP_200_OK  # Cannot edit source if used
        obj.refresh_from_db()
        assert obj.source.size == self.get_example_object1().size
        assert obj.source.read() == self.get_example_object1().read()
        assert obj.title == "Test Image"
        assert obj.scale == "2.00 2.00"
        assert obj.position == "0 1 0"
        assert obj.author == "Old Author"
        assert obj.owner == self.profile

    def test_can_edit_object_attributes_if_used_by_other(self):
        """Test that the object attributes can be edited if it is used by another user. Except the source file."""

        obj = ObjectFactory(
            title="Test Image",
            source=self.get_example_object1(),
            scale="2 1",
            position="0 1 0",
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
                "scale": "3.0",
                "position": "3 2 1",
                "author": "new author",
            },
        )
        assert response.status_code == status.HTTP_302_FOUND
        obj.refresh_from_db()
        assert obj.title == "new title"
        assert obj.source.size == self.get_example_object1().size
        assert obj.source.read() == self.get_example_object1().read()
        assert obj.scale == "3.00 3.00"
        assert obj.position == "3 2 1"
        assert obj.author == "new author"
        assert obj.owner == self.profile
