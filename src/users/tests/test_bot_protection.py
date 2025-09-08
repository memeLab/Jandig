"""Test common bot attacks on user pages"""

from unittest.mock import Mock, patch

from django.test import TestCase, override_settings
from django.urls import reverse


class TestInvalidSignup(TestCase):
    @override_settings(RECAPTCHA_ENABLED=True)
    def test_invalid_signup(self):
        # Test invalid signup without recaptcha enabled but without token should return 400
        response = self.client.post(
            reverse("signup"),
            {"username": "test", "password1": "test", "password2": "test"},
        )
        self.assertEqual(response.status_code, 400)

        # Signup with an invalid g-recaptcha-response token should return 400
        with patch("requests.post") as mock_create_assessment:
            mock_create_assessment.return_value = Mock()
            mock_create_assessment.return_value.json.return_value = {
                "tokenProperties": {
                    "valid": False,
                    "invalidReason": "invalid token sent",
                }
            }

            response = self.client.post(
                reverse("signup"),
                {
                    "username": "test",
                    "password1": "test",
                    "password2": "test",
                    "g-recaptcha-response": "DFwmgvoqhXuFGd",
                },
            )
            self.assertEqual(response.status_code, 400)

    @override_settings(RECAPTCHA_ENABLED=True)
    def test_invalid_action(self):
        # Test invalid signup without recaptcha enabled but without token should return 400
        response = self.client.post(
            reverse("signup"),
            {"username": "test", "password1": "test", "password2": "test"},
        )
        self.assertEqual(response.status_code, 400)

        # Signup with an invalid g-recaptcha-response token should return 400
        with patch("requests.post") as mock_create_assessment:
            mock_create_assessment.return_value = Mock()
            mock_create_assessment.return_value.json.return_value = {
                "tokenProperties": {
                    "valid": True,
                    "action": "different_action",
                }
            }

            response = self.client.post(
                reverse("signup"),
                {
                    "username": "test",
                    "password1": "test",
                    "password2": "test",
                    "g-recaptcha-response": "DFwmgvoqhXuFGd",
                },
            )
            self.assertEqual(response.status_code, 400)

    @override_settings(RECAPTCHA_ENABLED=True)
    def test_low_recaptcha_score(self):
        with patch("requests.post") as mock_create_assessment:
            mock_create_assessment.return_value = Mock()
            mock_create_assessment.return_value.json.return_value = {
                "tokenProperties": {
                    "valid": True,
                    "action": "sign_up",
                },
                "riskAnalysis": {
                    "score": 0.1,
                    "reasons": ["AUTOMATION", "TOO_MUCH_TRAFFIC"],
                },
                "name": "google cloud project assessment name",
            }

            response = self.client.post(
                reverse("signup"),
                {
                    "username": "test",
                    "password1": "test",
                    "password2": "test",
                    "g-recaptcha-response": "DFwmgvoqhXuFGd",
                },
            )
            self.assertEqual(response.status_code, 400)
