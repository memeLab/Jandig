import factory

from django.test import TestCase, Client, RequestFactory
from unittest import mock

from .views import recover_password
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
        request = self.client_test.post('/recover/', {'username_or_email': 'test2019ador@gmail.com'}, follow=True)
        response = recover_password(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/users/invalid-recovering-email')

    def test_recover_password_invalid_username(self):
        request = self.client_test.post('/recover/', {'username_or_email': 'testador'}, follow=True)
        response = recover_password(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/users/invalid-recovering-email')

    def test_recover_password_valid_email(self):
        request = self.client_test.post('/recover/', {'username_or_email': 'test2019ador@gmail.com'}, follow=True)
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