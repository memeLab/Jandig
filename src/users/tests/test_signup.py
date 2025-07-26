from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

DEFAULT_VALID_PASSWORD = "Aa#12C34d6561"


class TestSignup(TestCase):
    def test_signup(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "test",
                "email": "test@example.com",
                "password1": DEFAULT_VALID_PASSWORD,
                "password2": DEFAULT_VALID_PASSWORD,
            },
        )
        # Redirected to the profile page after successful signup
        assert response.status_code == 302
        user = get_user_model().objects.get(username="test")
        assert user.email == "test@example.com"

    def test_signup_with_repeated_email(self):
        # First signup
        response = self.client.post(
            reverse("signup"),
            {
                "username": "test",
                "email": "test@example.com",
                "password1": DEFAULT_VALID_PASSWORD,
                "password2": DEFAULT_VALID_PASSWORD,
            },
        )
        assert response.status_code == 302
        user = get_user_model().objects.get(username="test")
        assert user.email == "test@example.com"
        # Second signup with the same email
        response = self.client.post(
            reverse("signup"),
            {
                "username": "test",
                "email": "test@example.com",
                "password1": DEFAULT_VALID_PASSWORD,
                "password2": DEFAULT_VALID_PASSWORD,
            },
        )
        # Not redirected, should return with 200 to show the form again and errors
        assert response.status_code == 200
        assert "E-mail taken" in response.content.decode()

    def test_signup_with_invalid_email(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "test",
                "email": "invalid-email",
                "password1": DEFAULT_VALID_PASSWORD,
                "password2": DEFAULT_VALID_PASSWORD,
            },
        )
        # Not redirected, should return with 200 to show the form again and errors
        assert response.status_code == 200
        assert "Enter a valid email address." in response.content.decode()

    def test_signup_with_short_password(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "test",
                "email": "test@example.com",
                "password1": "short",
                "password2": "short",
            },
        )
        # Not redirected, should return with 200 to show the form again and errors
        assert response.status_code == 200
        assert "This password is too short." in response.content.decode()

    def test_signup_with_mismatched_passwords(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "test",
                "email": "test@example.com",
                "password1": DEFAULT_VALID_PASSWORD,
                "password2": "a#12C34d6561",
            },
        )
        # Not redirected, should return with 200 to show the form again and errors
        assert response.status_code == 200
        assert "The two password fields didn’t match." in response.content.decode()

    def test_signup_with_existing_username(self):
        # First signup
        response = self.client.post(
            reverse("signup"),
            {
                "username": "test",
                "email": "test@example.com",
                "password1": DEFAULT_VALID_PASSWORD,
                "password2": DEFAULT_VALID_PASSWORD,
            },
        )
        assert response.status_code == 302
        user = get_user_model().objects.get(username="test")
        assert user.email == "test@example.com"
        # Second signup with the same username
        response = self.client.post(
            reverse("signup"),
            {
                "username": "test",
                "email": "test2@example.com",
                "password1": DEFAULT_VALID_PASSWORD,
                "password2": DEFAULT_VALID_PASSWORD,
            },
        )
        # Not redirected, should return with 200 to show the form again and errors
        assert response.status_code == 200
        assert "A user with that username already exists." in response.content.decode()

    def test_signup_with_case_sensitive_username(self):
        # First signup
        response = self.client.post(
            reverse("signup"),
            {
                "username": "TestUser",
                "email": "test@example.com",
                "password1": DEFAULT_VALID_PASSWORD,
                "password2": DEFAULT_VALID_PASSWORD,
            },
        )
        assert response.status_code == 302
        user = get_user_model().objects.get(username="TestUser")
        assert user.email == "test@example.com"
        # Second signup with the same username but different case
        response = self.client.post(
            reverse("signup"),
            {
                "username": "testuser",
                "email": "test2@example.com",
                "password1": DEFAULT_VALID_PASSWORD,
                "password2": DEFAULT_VALID_PASSWORD,
            },
        )
        # Not redirected, should return with 200 to show the form again and errors
        assert response.status_code == 200
        assert "A user with that username already exists." in response.content.decode()

    def test_case_sensitive_email(self):
        # First signup
        response = self.client.post(
            reverse("signup"),
            {
                "username": "test",
                "email": "Test@Example.com",
                "password1": DEFAULT_VALID_PASSWORD,
                "password2": DEFAULT_VALID_PASSWORD,
            },
        )
        assert response.status_code == 302
        user = get_user_model().objects.get(username="test")
        assert user.email == "Test@example.com"
        # Second signup with the same email but different case
        response = self.client.post(
            reverse("signup"),
            {
                "username": "test2",
                "email": "test@example.com",
                "password1": DEFAULT_VALID_PASSWORD,
                "password2": DEFAULT_VALID_PASSWORD,
            },
        )
        # Not redirected, should return with 200 to show the form again and errors
        assert response.status_code == 200
        assert "E-mail taken" in response.content.decode()

    def test_case_sensitive_email_and_username(self):
        # First signup
        response = self.client.post(
            reverse("signup"),
            {
                "username": "TestUser",
                "email": "Test@Example.com",
                "password1": DEFAULT_VALID_PASSWORD,
                "password2": DEFAULT_VALID_PASSWORD,
            },
        )
        assert response.status_code == 302
        user = get_user_model().objects.get(username="TestUser")
        assert user.email == "Test@example.com"
        # Second signup with the same email and username but different case
        response = self.client.post(
            reverse("signup"),
            {
                "username": "testuser",
                "email": "test@example.com",
                "password1": DEFAULT_VALID_PASSWORD,
                "password2": DEFAULT_VALID_PASSWORD,
            },
        )
        # Not redirected, should return with 200 to show the form again and errors
        assert response.status_code == 200
        assert "A user with that username already exists." in response.content.decode()
        assert "E-mail taken" in response.content.decode()

    def test_signup_with_username_with_special_characters(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "test_user!@#",
                "email": "test_user@example.com",
                "password1": DEFAULT_VALID_PASSWORD,
                "password2": DEFAULT_VALID_PASSWORD,
            },
        )
        # Not redirected, should return with 200 to show the form again and errors
        assert response.status_code == 200
        assert "Enter a valid username." in response.content.decode()

    def test_signup_with_username_with_20_characters(self):
        data = {
            "username": "testuser1234567890123",
            "email": "testuser@example.com",
            "password1": DEFAULT_VALID_PASSWORD,
            "password2": DEFAULT_VALID_PASSWORD,
        }
        response = self.client.post(
            reverse("signup"),
            data,
        )
        # Not redirected, should return with 200 to show the form again and errors
        assert response.status_code == 200
        assert (
            "Ensure this value has at most 20 characters (it has 21)."
            in response.content.decode()
        )

        data["username"] = "testuser123456789012"
        response = self.client.post(
            reverse("signup"),
            data,
        )
        # Should be successful with 20 characters
        assert response.status_code == 302
        user = get_user_model().objects.get(username="testuser123456789012")
        assert user.email == "testuser@example.com"
        assert user.check_password(DEFAULT_VALID_PASSWORD)
