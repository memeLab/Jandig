from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse


class TestResetPassword(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="Aa#12C34d6561",
        )

    def test_reset_password_invalid_email_shows_error(self):
        """An invalid email should re-render the form with its error"""
        response = self.client.post(
            reverse("reset-password"), {"email": "not-an-email"}
        )
        assert response.status_code == 200
        assert "Enter a valid email address." in response.content.decode()
        assert len(mail.outbox) == 0

    def test_reset_password_sends_email(self):
        """A registered email should receive the reset link"""
        response = self.client.post(
            reverse("reset-password"), {"email": "test@example.com"}
        )
        assert response.status_code == 302
        assert response.url == reverse("home")
        assert len(mail.outbox) == 1
        message = mail.outbox[0]
        assert message.to == ["test@example.com"]
        assert message.subject == "Jandig Password Reset"
        assert "your test@example.com Jandig account" in message.body
        assert "/password-reset-confirm/" in message.body
