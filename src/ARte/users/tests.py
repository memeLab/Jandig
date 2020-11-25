import factory

from django.test import TestCase, Client, RequestFactory
from unittest import mock

from .views import edit_object
from .factory import ObjectFactory

class EditObjectTestCase(TestCase):
    def setUp(self):
        self.client_test = RequestFactory()

    def test_redirect_to_edit_object_page(self):
        # request = self.client_test.get('/objects/edit/', follow=True)
        # response = edit_object(request)
        # self.assertEqual(response.status_code, 200)
        pass

    def test_edit_object_title(self):
        pass

    def test_edit_object_image(self):
        pass

    def test_edit_object_scale(self):
        pass

    def test_edit_object_position(self):
        pass