"""Test common bot attacks on user pages"""

from unittest.mock import Mock, patch

from django.test import TestCase, override_settings
from django.urls import reverse


class TestInvalidSignup(TestCase):
    @override_settings(TURNSTILE_ENABLED=True)
    def test_missing_turnstile_token(self):
        # Signup without cf-turnstile-response token should return 400
        response = self.client.post(
            reverse("signup"),
            {"username": "test", "password1": "test", "password2": "test"},
        )
        self.assertEqual(response.status_code, 400)

    @override_settings(TURNSTILE_ENABLED=True)
    def test_invalid_turnstile_token(self):
        # Signup with a token that fails verification should return 400
        with patch("users.services.turnstile_service.requests.post") as mock_post:
            mock_post.return_value = Mock()
            mock_post.return_value.json.return_value = {"success": False}

            response = self.client.post(
                reverse("signup"),
                {
                    "username": "test",
                    "password1": "test",
                    "password2": "test",
                    "cf-turnstile-response": "invalid-token",
                },
            )
            self.assertEqual(response.status_code, 400)

    @override_settings(TURNSTILE_ENABLED=False)
    def test_turnstile_disabled_skips_verification(self):
        # When turnstile is disabled, signup should not require a token
        response = self.client.post(
            reverse("signup"),
            {
                "username": "testuser",
                "password1": "Str0ngP@ss!",
                "password2": "Str0ngP@ss!",
            },
        )
        # Should not return 400 for missing token
        self.assertNotEqual(response.status_code, 400)
