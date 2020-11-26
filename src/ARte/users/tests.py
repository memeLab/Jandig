import factory

from django.test import TestCase, Client, RequestFactory
from unittest import mock

from .factory import ObjectFactory, UserFactory
from .views import edit_object

class EditObjectTestCase(TestCase):
    def setUp(self):
        self.client_test = RequestFactory()

    def test_redirect(self):
        request = self.client_test.get('objects/edit', follow=True)
        response = edit_object(request)
        self.assertEqual(response.status_code, 200)