from django.test import TestCase, RequestFactory
from unittest import mock
from .views import edit_object, recover_password
from .services.email_service import EmailService
from .services.encrypt_service import EncryptService
from .services.user_service import UserService
from .factory import UserFactory


class UserTestCase(TestCase):
    def setUp(self):
        self.client_test = RequestFactory()
        self.email_service = EmailService("You have requested a new password.")
        self.encrypt_service = EncryptService()
        self.user_service = UserService()

        self.request = self.client_test.get("/recover/", follow=True)

    def test_redirect_to_recover_password_page(self):
        response = recover_password(self.request)
        self.assertEqual(response.status_code, 200)

    def test_recover_password_invalid_email(self):
        request = self.client_test.post(
            "/recover/",
            {"username_or_email": "testadorinvalid@memelab.com"},
            follow=True,
        )
        response = recover_password(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/users/invalid-recovering-email")

    def test_recover_password_invalid_username(self):
        request = self.client_test.post(
            "/recover/", {"username_or_email": "testadorinvalid"}, follow=True
        )
        response = recover_password(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/users/invalid-recovering-email")

    def test_recover_password_valid_email(self):
        request = self.client_test.post(
            "/recover/", {"username_or_email": "testador@memelab.com"}, follow=True
        )
        UserFactory()
        response = recover_password(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/users/recover-code/")

    def test_recover_password_valid_username(self):
        request = self.client_test.post(
            "/recover/", {"username_or_email": "Testador"}, follow=True
        )
        UserFactory()
        response = recover_password(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/users/recover-code/")

    def test_build_multipart_message(self):
        email = "testador@memelab.com"
        response = self.email_service.build_multipart_message(email)
        self.assertEquals(response["From"], "jandig@memelab.com.br")
        self.assertEquals(response["To"], email)

    @mock.patch("users.services.email_service.smtplib.SMTP.quit")
    def test_send_email_to_recover_password(self, mock_quit):
        email = "testador@memelab.com"
        response = self.email_service.build_multipart_message(email)
        self.email_service.send_email_to_recover_password(response)
        mock_quit.assert_called_once()

    @mock.patch("users.services.encrypt_service.EncryptService.generate_hash_code")
    def test_generate_verification_code(self, mock_hash):
        email = "testador@memelab.com"
        self.encrypt_service.generate_verification_code(email)
        mock_hash.assert_called_once()

    def test_check_if_username_or_email_exist(self):
        email = "testador@memelab.com"
        UserFactory()
        response = self.user_service.check_if_username_or_email_exist(email)
        self.assertTrue(response)

    def test_check_if_username_or_email_doesnt_exist(self):
        email = "testadorinvalido@memelab.com"
        UserFactory()
        response = self.user_service.check_if_username_or_email_exist(email)
        self.assertFalse(response)

    def test_get_user_email_by_email(self):
        email = "testador@memelab.com"
        UserFactory()
        response = self.user_service.get_user_email(email)
        self.assertEquals(response, email)

    def test_get_user_email_by_username(self):
        username = "Testador"
        UserFactory()
        response = self.user_service.get_user_email(username)
        self.assertEquals(response, "testador@memelab.com")


class EditObjectTestCase(TestCase):
    def setUp(self):
        self.client_test = RequestFactory()

    def test_redirect(self):
        request = self.client_test.get("objects/edit", follow=True)
        response = edit_object(request)
        self.assertEqual(response.status_code, 200)
