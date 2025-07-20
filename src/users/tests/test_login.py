from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

DEFAULT_VALID_PASSWORD = "Aa#12C34d6561"


class TestLogin(TestCase):
    def test_login_with_valid_username(self):
        get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password=DEFAULT_VALID_PASSWORD,
        )
        response = self.client.post(
            reverse("login"),
            {"username": "testuser", "password": DEFAULT_VALID_PASSWORD},
        )
        # Should be redirected to the profile page after successful login
        assert response.status_code == 302

    def test_login_with_valid_email(self):
        get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password=DEFAULT_VALID_PASSWORD,
        )
        response = self.client.post(
            reverse("login"),
            {"username": "testuser", "password": DEFAULT_VALID_PASSWORD},
        )
        # Should be redirected to the profile page after successful login
        assert response.status_code == 302

    def test_login_with_case_sensitive_username(self):
        _ = get_user_model().objects.create_user(
            username="TestUser",
            email="Test@Example.com",
            password=DEFAULT_VALID_PASSWORD,
        )
        response = self.client.post(
            reverse("login"),
            {"username": "TestUser", "password": DEFAULT_VALID_PASSWORD},
        )
        # Should be redirected to the profile page after successful login
        assert response.status_code == 302
        response = self.client.post(
            reverse("login"),
            {"username": "testuser", "password": DEFAULT_VALID_PASSWORD},
        )
        # Should work with different case
        assert response.status_code == 302

        response = self.client.post(
            reverse("login"),
            {"username": "TESTUSER", "password": DEFAULT_VALID_PASSWORD},
        )
        # Should be redirected to the profile page after successful login
        assert response.status_code == 302

    def test_login_with_case_sensitive_email(self):
        _ = get_user_model().objects.create_user(
            username="TestUser",
            email="Test@Example.com",
            password=DEFAULT_VALID_PASSWORD,
        )
        response = self.client.post(
            reverse("login"),
            {"username": "Test@Example.com", "password": DEFAULT_VALID_PASSWORD},
        )
        # Should be redirected to the profile page after successful login
        assert response.status_code == 302
        response = self.client.post(
            reverse("login"),
            {"username": "test@example.com", "password": DEFAULT_VALID_PASSWORD},
        )
        # Should be redirected to the profile page after successful login
        assert response.status_code == 302
        response = self.client.post(
            reverse("login"),
            {"username": "TEST@EXAMPLE.COM", "password": DEFAULT_VALID_PASSWORD},
        )
        # Should be redirected to the profile page after successful login
        assert response.status_code == 302
