from django.test import TestCase, RequestFactory
from unittest import mock, skip
from .views import edit_object, recover_password
from .services.email_service import EmailService
from .services.encrypt_service import EncryptService
from .services.user_service import UserService
from .factory import UserFactory
from django.shortcuts import redirect


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


    @skip("demonstrating skipping")
    def test_recover_password_valid_email(self):
        request = self.client_test.post(
            "/recover/", {"username_or_email": "testador@memelab.com"}, follow=True
        )
        UserFactory()
        response = recover_password(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/users/recover-code/")

    @skip("demonstrating skipping")
    def test_recover_password_valid_username(self):
        request = self.client_test.post(
            "/recover/", {"username_or_email": "Testador"}, follow=True
        )
        UserFactory()
        response = recover_password(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/users/recover-code/") 

    @mock.patch("users.services.email_service.EmailService.build_multipart_message", return_value={"From": "jandig@memelab.com.br", "To": "testador@memelab.com"})
    def test_build_multipart_message(self, mock_mail):
        email = "testador@memelab.com"
        response = self.email_service.build_multipart_message(email)
        self.assertEqual(response["From"], "jandig@memelab.com.br")
        self.assertEqual(response["To"], email) 
        mock_mail.assert_called_once()

    @mock.patch("users.services.email_service.EmailService.send_email_to_recover_password")
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

    @mock.patch("users.services.user_service.UserService.check_if_username_or_email_exist")
    def test_check_if_username_or_email_exist(self, mock_check):
        email = "testador@memelab.com"
        UserFactory()
        response = self.user_service.check_if_username_or_email_exist(email)
        self.assertTrue(response)
        mock_check.assert_called_once() 

    @mock.patch("users.services.user_service.UserService.check_if_username_or_email_exist", return_value=False)
    def test_check_if_username_or_email_doesnt_exist(self, mock_check):
        email = "testadorinvalido@memelab.com"
        UserFactory()
        response = self.user_service.check_if_username_or_email_exist(email)
        self.assertFalse(response)
        mock_check.assert_called_once() 
 
    @mock.patch("users.services.user_service.UserService.get_user_email", return_value="testador@memelab.com")
    def test_get_user_email_by_email(self, mock_get_user):
        email = "testador@memelab.com"
        UserFactory()
        response = self.user_service.get_user_email(email)
        self.assertEqual(response, email) 
        mock_get_user.assert_called_once()

    @mock.patch("users.services.user_service.UserService.get_user_email", return_value="testador@memelab.com")
    def test_get_user_email_by_username(self, mock_get_user):
        username = "Testador"
        UserFactory()
        response = self.user_service.get_user_email(username)
        self.assertEqual(response, "testador@memelab.com")
        mock_get_user.assert_called_once()
 
class EditObjectTestCase(TestCase):
    def setUp(self):
        self.client_test = RequestFactory()

    @skip("demonstrating skipping")
    def test_redirect(self):
        request = self.client_test.get("objects/edit", follow=True)
        response = edit_object(request)
        self.assertEqual(response.status_code, 200)
