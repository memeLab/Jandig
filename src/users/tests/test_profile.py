from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

DEFAULT_VALID_PASSWORD = "Aa#12C34d6561"


class TestProfile(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password=DEFAULT_VALID_PASSWORD,
        )

    def test_profile_get_not_authenticated(self):
        """Profile page should not be reachable by get"""
        response = self.client.get(reverse("profile"))
        assert response.status_code == 302  # Redirect to login
        assert response.url == reverse("login") + "?next=" + reverse("profile")

    def test_profile_get_authenticated(self):
        """Profile page should be reachable by get"""
        self.client.login(username="testuser", password=DEFAULT_VALID_PASSWORD)
        response = self.client.get(reverse("profile"))
        assert response.status_code == 200
        profile = self.user.profile
        assert profile.artworks_count == 0
        assert profile.markers_count == 0
        assert profile.ar_objects_count == 0
        assert profile.exhibits_count == 0
        assert str(profile) == f"{profile.id}"
