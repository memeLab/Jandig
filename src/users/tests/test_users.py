from unittest import mock

from django.test import RequestFactory, TestCase

from users.factory import UserFactory
from users.services.email_service import EmailService
from users.services.encrypt_service import EncryptService
from users.services.user_service import UserService
from users.views import recover_password


@mock.patch("smtplib.SMTP.quit")
@mock.patch("smtplib.SMTP.login", side_effect=lambda *args, **kwargs: None)
@mock.patch("smtplib.SMTP.sendmail", side_effect=lambda *args, **kwargs: None)
class UserTestCase(TestCase):
    def setUp(self):
        self.client_test = RequestFactory()
        self.email_service = EmailService("You have requested a new password.")
        self.encrypt_service = EncryptService()
        self.user_service = UserService()

    def test_redirect_to_recover_password_page(self, *args, **kwargs):
        request = self.client_test.get("/recover/", follow=True)
        response = recover_password(request)
        self.assertEqual(response.status_code, 200)

    def test_recover_password_invalid_email(self, *args, **kwargs):
        request = self.client_test.post(
            "/recover/",
            {"username_or_email": "testadorinvalid@memelab.com"},
            follow=True,
        )
        response = recover_password(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/users/invalid-recovering-email")

    def test_recover_password_invalid_username(self, *args, **kwargs):
        request = self.client_test.post(
            "/recover/", {"username_or_email": "testadorinvalid"}, follow=True
        )
        response = recover_password(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/users/invalid-recovering-email")

    def test_recover_password_valid_email(self, *args, **kwargs):
        request = self.client_test.post(
            "/recover/", {"username_or_email": "testador@memelab.com"}, follow=True
        )
        UserFactory()
        response = recover_password(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/users/recover-code/")

    def test_recover_password_valid_username(self, *args, **kwargs):
        request = self.client_test.post(
            "/recover/", {"username_or_email": "Testador"}, follow=True
        )
        UserFactory()
        response = recover_password(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/users/recover-code/")

    def test_build_multipart_message(self, *args, **kwargs):
        email = "testador@memelab.com"
        response = self.email_service.build_multipart_message(email)
        self.assertEqual(response["From"], "Jandig <jandig@jandig.com>")
        self.assertEqual(response["To"], email)

    def test_send_email_to_recover_password(self, mock_quit, *args, **kwargs):
        email = "testador@memelab.com"
        response = self.email_service.build_multipart_message(email)
        self.email_service.send_email_to_recover_password(response)
        mock_quit.assert_called_once()

    @mock.patch("users.services.encrypt_service.EncryptService.generate_hash_code")
    def test_generate_verification_code(self, mock_hash, *args, **kwargs):
        email = "testador@memelab.com"
        self.encrypt_service.generate_verification_code(email)
        mock_hash.assert_called_once()

    def test_check_if_username_or_email_exist(self, *args, **kwargs):
        email = "testador@memelab.com"
        UserFactory()
        response = self.user_service.check_if_username_or_email_exist(email)
        self.assertTrue(response)

    def test_check_if_username_or_email_doesnt_exist(self, *args, **kwargs):
        email = "testadorinvalido@memelab.com"
        UserFactory()
        response = self.user_service.check_if_username_or_email_exist(email)
        self.assertFalse(response)

    def test_get_user_email_by_email(self, *args, **kwargs):
        email = "testador@memelab.com"
        UserFactory()
        response = self.user_service.get_user_email(email)
        self.assertEqual(response, email)

    def test_get_user_email_by_username(self, *args, **kwargs):
        username = "Testador"
        UserFactory()
        response = self.user_service.get_user_email(username)
        self.assertEqual(response, "testador@memelab.com")
