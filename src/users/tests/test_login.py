from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

DEFAULT_VALID_PASSWORD = "Aa#12C34d6561"


class TestLogin(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.email = "test@example.com"
        self.user = get_user_model().objects.create_user(
            username=self.username,
            email=self.email,
            password=DEFAULT_VALID_PASSWORD,
        )

    def test_login_with_valid_username(self):
        response = self.client.post(
            reverse("login"),
            {"username": self.username, "password": DEFAULT_VALID_PASSWORD},
        )
        # Should be redirected to the profile page after successful login
        assert response.status_code == 302

    def test_login_with_valid_email(self):
        response = self.client.post(
            reverse("login"),
            {"username": self.email, "password": DEFAULT_VALID_PASSWORD},
        )
        # Should be redirected to the profile page after successful login
        assert response.status_code == 302

    def test_login_with_case_sensitive_username(self):
        _ = get_user_model().objects.create_user(
            username="TestUser2",
            email="Test2@Example.com",
            password=DEFAULT_VALID_PASSWORD,
        )
        response = self.client.post(
            reverse("login"),
            {"username": "TestUser2", "password": DEFAULT_VALID_PASSWORD},
        )
        # Should be redirected to the profile page after successful login
        assert response.status_code == 302
        response = self.client.post(
            reverse("login"),
            {"username": "testuser2", "password": DEFAULT_VALID_PASSWORD},
        )
        # Should work with different case
        assert response.status_code == 302

        response = self.client.post(
            reverse("login"),
            {"username": "TESTUSER2", "password": DEFAULT_VALID_PASSWORD},
        )
        # Should be redirected to the profile page after successful login
        assert response.status_code == 302

    def test_login_with_case_sensitive_email(self):
        _ = get_user_model().objects.create_user(
            username="TestUser2",
            email="Test2@Example.com",
            password=DEFAULT_VALID_PASSWORD,
        )
        response = self.client.post(
            reverse("login"),
            {"username": "Test2@Example.com", "password": DEFAULT_VALID_PASSWORD},
        )
        # Should be redirected to the profile page after successful login
        assert response.status_code == 302
        response = self.client.post(
            reverse("login"),
            {"username": "test2@example.com", "password": DEFAULT_VALID_PASSWORD},
        )
        # Should be redirected to the profile page after successful login
        assert response.status_code == 302
        response = self.client.post(
            reverse("login"),
            {"username": "TEST2@EXAMPLE.COM", "password": DEFAULT_VALID_PASSWORD},
        )
        # Should be redirected to the profile page after successful login
        assert response.status_code == 302

    def test_login_with_invalid_username(self):
        response = self.client.post(
            reverse("login"),
            {"username": "invaliduser", "password": DEFAULT_VALID_PASSWORD},
        )
        # Should return to login page with error
        assert response.status_code == 200
        assert "Username/email not found" in response.content.decode()

    def test_login_with_invalid_email(self):
        response = self.client.post(
            reverse("login"),
            {"username": "invalid@example.com", "password": DEFAULT_VALID_PASSWORD},
        )
        # Should return to login page with error
        assert response.status_code == 200
        assert "Username/email not found" in response.content.decode()

    def test_login_with_invalid_password(self):
        response = self.client.post(
            reverse("login"),
            {"username": self.username, "password": "WrongPassword123"},
        )
        # Should return to login page with error
        assert response.status_code == 200
        assert "Wrong password!" in response.content.decode()
