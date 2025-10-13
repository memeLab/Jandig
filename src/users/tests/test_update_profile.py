from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

DEFAULT_VALID_PASSWORD = "Aa#12C34d6561"


class TestUpdateProfile(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password=DEFAULT_VALID_PASSWORD,
        )

    def test_update_profile_get_not_authenticated(self):
        """Update profile page should not be reachable by get"""
        response = self.client.get(reverse("edit-profile"))
        assert response.status_code == 302  # Redirect to login
        assert response.url == reverse("login") + "?next=" + reverse("edit-profile")

    def test_update_profile_get_authenticated(self):
        """Update profile page should be reachable by get"""
        self.client.login(username="testuser", password=DEFAULT_VALID_PASSWORD)
        response = self.client.get(reverse("edit-profile"))
        assert response.status_code == 200

    def test_update_profile_success_post(self):
        """Update profile with valid data should succeed"""
        self.client.login(username="testuser", password=DEFAULT_VALID_PASSWORD)
        response = self.client.post(
            reverse("edit-profile"),
            {
                "username": "new_username",
                "email": "new_email@example.com",
                "bio": "This is my new bio.",
                "country": "AZ",
                "personal_site": "https://example.com",
            },
        )
        assert response.status_code == 302
        self.user.refresh_from_db()
        assert self.user.username == "new_username"
        assert self.user.email == "new_email@example.com"
        assert self.user.profile.bio == "This is my new bio."
        assert self.user.profile.country == "AZ"
        assert self.user.profile.personal_site == "https://example.com"

    def test_update_profile_repeated_username_post(self):
        """Update profile with repeated username should fail"""
        get_user_model().objects.create_user(
            username="existinguser",
            email="existing@example.com",
            password=DEFAULT_VALID_PASSWORD,
        )
        self.client.login(username="testuser", password=DEFAULT_VALID_PASSWORD)
        response = self.client.post(
            reverse("edit-profile"),
            {
                "username": "existinguser",
                "email": "new_email@example.com",
                "bio": "This is my new bio.",
                "country": "AZ",
                "personal_site": "https://example.com",
            },
        )
        assert response.status_code == 200
        assert "Username already in use" in response.content.decode()

    def test_update_profile_repeated_email_post(self):
        """Update profile with repeated email should fail"""
        get_user_model().objects.create_user(
            username="existinguser",
            email="existing@example.com",
            password=DEFAULT_VALID_PASSWORD,
        )
        self.client.login(username="testuser", password=DEFAULT_VALID_PASSWORD)
        response = self.client.post(
            reverse("edit-profile"),
            {
                "username": "new_username",
                "email": "existing@example.com",
                "bio": "This is my new bio.",
                "country": "AZ",
                "personal_site": "https://example.com",
            },
        )
        assert response.status_code == 200
        assert "Email address must be unique" in response.content.decode()
