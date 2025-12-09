from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

DEFAULT_VALID_PASSWORD = "Aa#12C34d6561"


class TestChangePassword(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password=DEFAULT_VALID_PASSWORD,
        )

    def test_change_password_get_not_authenticated(self):
        """Change password page should not be reachable by get"""
        response = self.client.get(reverse("edit-password"))
        assert response.status_code == 302  # Redirect to login
        assert response.url == reverse("login") + "?next=" + reverse("edit-password")

    def test_change_password_get_authenticated(self):
        """Change password page should not be reachable by get"""
        self.client.login(username="testuser", password=DEFAULT_VALID_PASSWORD)
        response = self.client.get(reverse("edit-password"))
        assert response.status_code == 404

    def test_change_password_success_post(self):
        """Change password with valid data should succeed"""
        self.client.login(username="testuser", password=DEFAULT_VALID_PASSWORD)
        response = self.client.post(
            reverse("edit-password"),
            {
                "old_password": DEFAULT_VALID_PASSWORD,
                "new_password1": "NewPassword123!",
                "new_password2": "NewPassword123!",
            },
        )
        assert response.status_code == 302
        self.user.refresh_from_db()
        assert self.user.check_password("NewPassword123!")

    def test_change_password_failure_post(self):
        """Change password with invalid data should fail"""
        self.client.login(username="testuser", password=DEFAULT_VALID_PASSWORD)
        response = self.client.post(
            reverse("edit-password"),
            {
                "old_password": DEFAULT_VALID_PASSWORD,
                "new_password1": "NewPassword123!",
                "new_password2": "NewPassword1!",
            },
        )
        assert response.status_code == 200
        self.user.refresh_from_db()
        assert self.user.check_password(DEFAULT_VALID_PASSWORD)
