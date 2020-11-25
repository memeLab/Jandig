import factory

from django.test import TestCase, Client, RequestFactory
from unittest import mock

from .views import recover_password, build_multipart_message, send_email_to_recover_password, generate_verification_code, generate_hash_code, check_if_username_or_email_exist, get_user_email
from .factory import UserFactory

# Create your tests here.
class UserTestCase(TestCase):
    def setUp(self):
        self.client_test = RequestFactory()
    
    def test_redirect_to_recover_password_page(self):
        request = self.client_test.get('/recover/', follow=True)
        response = recover_password(request)
        self.assertEqual(response.status_code, 200)

    def test_recover_password_invalid_email(self):
        request = self.client_test.post('/recover/', {'username_or_email': 'testadorinvalid@memelab.com'}, follow=True)
        response = recover_password(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/users/invalid-recovering-email')

    def test_recover_password_invalid_username(self):
        request = self.client_test.post('/recover/', {'username_or_email': 'testadorinvalid'}, follow=True)
        response = recover_password(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/users/invalid-recovering-email')

    def test_recover_password_valid_email(self):
        request = self.client_test.post('/recover/', {'username_or_email': 'testador@memelab.com'}, follow=True)
        user_data = UserFactory()
        response = recover_password(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/users/recover-code/')

    def test_recover_password_valid_username(self):
        request = self.client_test.post('/recover/', {'username_or_email': 'Testador'}, follow=True)
        user_data = UserFactory()
        response = recover_password(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/users/recover-code/')

    def test_build_multipart_message(self):
        message = 'You have requested a new password.'
        email = "testador@memelab.com"
        response = build_multipart_message(email, message)
        self.assertEquals(response['From'], "jandig@memelab.com.br")
        self.assertEquals(response['To'], email)
    
    @mock.patch('users.views.smtplib.SMTP.quit')
    def test_send_email_to_recover_password(self, mock_quit):
        message = 'You have requested a new password.'
        email = "testador@memelab.com"
        response = build_multipart_message(email, message)
        send_email_to_recover_password(message, response)
        mock_quit.assert_called_once()
    
    @mock.patch('users.views.generate_hash_code')
    def test_generate_verification_code(self, mock_hash):
        email = "testador@memelab.com"
        generate_verification_code(email)
        mock_hash.assert_called_once()

    def test_generate_hash_code(self):
        decrypt_code = "2020112518493640967testador@memelab.comtestador@memelab.comtestador@memelab.comtestador@memelab.com"
        response = generate_hash_code(decrypt_code)
        self.assertEquals(response, "1c1a5df027f7ea6b126076cec241222b")
    
    def test_check_if_username_or_email_exist(self):
        email = "testador@memelab.com"
        user_data = UserFactory()
        response = check_if_username_or_email_exist(email)
        self.assertTrue(response)

    def test_check_if_username_or_email_doesnt_exist(self):
        email = "testadorinvalido@memelab.com"
        user_data = UserFactory()
        response = check_if_username_or_email_exist(email)
        self.assertFalse(response)

    def test_get_user_email_by_email(self):
        email = "testador@memelab.com"
        user_data = UserFactory()
        response = get_user_email(email)
        self.assertEquals(response, email)

    def test_get_user_email_by_username(self):
        username = "Testador"
        user_data = UserFactory()
        response = get_user_email(username)
        self.assertEquals(response, "testador@memelab.com")