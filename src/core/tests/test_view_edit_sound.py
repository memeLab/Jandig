from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from src.core.tests.factory import ArtworkFactory, SoundFactory
from src.core.tests.utils import get_example_sound
from src.users.tests.factory import ProfileFactory, UserFactory
from users.models import Profile, User

EXAMPLE_SOUND_PATH = "collection/sounds/happy-message-ping.mp3"
EXAMPLE_SOUND_FILE_SIZE = 36096  # Size in bytes of the example sound file


class TestSoundEdit(TestCase):
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

    def get_example_sound1(self):
        return get_example_sound("happy-message-ping.mp3")

    def get_example_sound2(self):
        return get_example_sound("sonar-ping.mp3")

    def test_edit_sound_unauthenticated(self):
        """Test that an unauthenticated user cannot access the edit object page."""
        url = reverse("edit-sound")
        response = self.client.get(url)
        assert response.status_code == status.HTTP_302_FOUND  # Redirect to login page
        assert "/users/login" in response.url

    def test_edit_sound_authenticated(self):
        """Test that an authenticated user can access the edit sound page."""
        self.client.login(username=self.username, password=self.password)
        sound = SoundFactory(
            title="Test Sound",
            file=self.get_example_sound1(),
            owner=self.profile,
        )
        url = reverse("edit-sound", query={"id": sound.id})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_edit_sound_as_another_user(self):
        """Test that a user cannot edit an sound they do not own."""
        sound = SoundFactory(
            title="Test Sound",
            file=self.get_example_sound1(),
            owner=self.profile,
        )

        another_user = User.objects.create_user(
            username="anotheruser",
            password="anotherpassword",
            is_staff=False,
            is_superuser=False,
        )
        # Log in as another user should not allow access to edit the sound
        self.client.login(username=another_user.username, password="anotherpassword")
        url = reverse("edit-sound", query={"id": sound.id})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Log in as the original user should allow access to edit the sound
        self.client.logout()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_edit_sound_title(self):
        """Test that the sound title can be edited."""
        self.client.login(username=self.username, password=self.password)

        sound = SoundFactory(
            title="Old Title",
            file=self.get_example_sound1(),
            owner=self.profile,
            author="Old Author",
        )
        url = reverse("edit-sound", query={"id": sound.id})
        response = self.client.post(
            url,
            {
                "title": "New Title",
                "file": sound.file,
                "author": sound.author,
            },
        )
        assert (
            response.status_code == status.HTTP_302_FOUND
        )  # Redirect after successful edit
        sound.refresh_from_db()
        assert sound.title == "New Title"
        # Compare two files by size and content
        assert sound.file.size == self.get_example_sound1().size
        assert sound.file.read() == self.get_example_sound1().read()
        assert sound.author == "Old Author"
        assert sound.owner == self.profile

    def test_edit_sound_author(self):
        """Test that the sound author can be edited."""
        self.client.login(username=self.username, password=self.password)

        sound = SoundFactory(
            title="Old Title",
            file=self.get_example_sound1(),
            owner=self.profile,
            author="Old Author",
        )
        url = reverse("edit-sound", query={"id": sound.id})
        response = self.client.post(
            url,
            {
                "title": sound.title,
                "file": sound.file,
                "author": "New Author",
            },
        )
        assert (
            response.status_code == status.HTTP_302_FOUND
        )  # Redirect after successful edit
        sound.refresh_from_db()
        assert sound.author == "New Author"
        assert sound.title == "Old Title"
        # Compare two files by size and content
        assert sound.file.size == self.get_example_sound1().size
        assert sound.file.read() == self.get_example_sound1().read()

        assert sound.owner == self.profile

    def test_edit_sound_file(self):
        """Test that the sound file can be edited."""
        self.client.login(username=self.username, password=self.password)

        sound = SoundFactory(
            title="Old Title",
            file=self.get_example_sound1(),
            owner=self.profile,
            author="Old Author",
        )
        url = reverse("edit-sound", query={"id": sound.id})
        new_file = self.get_example_sound2()
        response = self.client.post(
            url,
            {
                "title": sound.title,
                "file": new_file,
                "author": sound.author,
            },
        )
        assert response.status_code == status.HTTP_302_FOUND

    def test_edit_sound_if_used_by_self(self):
        """Test that a sound can be edited if it is used by the user."""
        self.client.login(username=self.username, password=self.password)
        # Create a base sound that the user owns
        sound = SoundFactory(
            title="Test Sound",
            file=self.get_example_sound1(),
            owner=self.profile,
            author="Old Author",
        )
        # Simulate the sound being used by the user
        _ = ArtworkFactory(
            title="Test Artwork",
            author=self.profile,
            sound=sound
        )

        url = reverse("edit-sound", query={"id": sound.id})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

        # Update every field
        response = self.client.post(
            url,
            {
                "title": "new title",
                "file": self.get_example_sound2(),
                "author": "new author",
            },
        )

        assert response.status_code == status.HTTP_302_FOUND
        sound.refresh_from_db()
        assert sound.title == "new title"
        assert sound.file.size == self.get_example_sound2().size
        assert sound.file.read() == self.get_example_sound2().read()
        assert sound.author == "new author"
        assert sound.owner == self.profile

    def test_cannot_edit_sound_file_if_used_by_other(self):
        """Test that a sound file cannot be edited if it is used by another user."""
        sound = SoundFactory(
            title="Test Sound",
            file=self.get_example_sound1(),
            owner=self.profile,
            author="Old Author",
        )

        # Simulate the sound being used by another user
        another_user = UserFactory(username="anotheruser", password="anotherpassword")
        another_profile = ProfileFactory(user=another_user)
        _ = ArtworkFactory(
            title="Test Artwork",
            author=another_profile,
            sound=sound
        )

        self.client.login(username=self.username, password=self.password)
        url = reverse("edit-sound", query={"id": sound.id})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        response = self.client.post(
            url,
            {
                "title": sound.title,
                "file": self.get_example_sound2(),
                "author": sound.author,
            },
        )
        assert response.status_code == status.HTTP_200_OK  # Cannot edit file if used
        sound.refresh_from_db()
        assert sound.file.size == self.get_example_sound1().size
        assert sound.file.read() == self.get_example_sound1().read()
        assert sound.title == "Test Sound"
        assert sound.author == "Old Author"
        assert sound.owner == self.profile

    def test_can_edit_sound_attributes_if_used_by_other(self):
        """Test that the sound attributes can be edited if it is used by another user. Except the file."""

        sound = SoundFactory(
            title="Test Sound",
            file=self.get_example_sound1(),
            owner=self.profile,
            author="Old Author",
        )

        # Simulate the object being used by another user
        another_user = UserFactory(username="anotheruser", password="anotherpassword")
        another_profile = ProfileFactory(user=another_user)
        _ = ArtworkFactory(
            title="Test Artwork",
            author=another_profile,
            sound=sound
        )

        self.client.login(username=self.username, password=self.password)
        url = reverse("edit-sound", query={"id": sound.id})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

        response = self.client.post(
            url,
            {
                "title": "new title",
                "file": self.get_example_sound1(),
                "author": "new author",
            },
        )
        assert response.status_code == status.HTTP_302_FOUND
        sound.refresh_from_db()
        assert sound.title == "new title"
        assert sound.file.size == self.get_example_sound1().size
        assert sound.file.read() == self.get_example_sound1().read()
        assert sound.author == "new author"
        assert sound.owner == self.profile
