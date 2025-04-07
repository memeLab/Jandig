"""Test common bot attacks on core pages"""

from django.test import TestCase


class TestInvalidIndex(TestCase):
    def test_invalid_index_on_exhibit_detail(self):
        # Test invalid index on exhibit detail should not raise exception and return 404
        response = self.client.get("/exhibit/?id=999")
        self.assertEqual(response.status_code, 404)

    def test_invalid_literal_on_exhibit_detail(self):
        # Test invalid literal on exhibit detail should not raise exception and return 404
        response = self.client.get("/exhibit/?id=%27")
        self.assertEqual(response.status_code, 404)
        response = self.client.get("/exhibit/?id=invalid")
        self.assertEqual(response.status_code, 404)
        response = self.client.get("/exhibit/?id='999'")
        self.assertEqual(response.status_code, 404)

    def test_empty_exhibit_id(self):
        # Test empty exhibit id should not raise exception and return 404
        response = self.client.get("/exhibit/?id=''")
        self.assertEqual(response.status_code, 404)
        response = self.client.get("/exhibit/?id=")
        self.assertEqual(response.status_code, 404)
        response = self.client.get("/exhibit/")
        self.assertEqual(response.status_code, 404)


    def test_invalid_exhibit_slug(self):
        # Test invalid exhibit
        response = self.client.get("/invalid")
        # Auto append slash will redirect to /invalid/
        self.assertEqual(response.status_code, 301)
        response = self.client.get("/invalid/")
        self.assertEqual(response.status_code, 404)
