"""Test sending push notifications for lockers"""
from unittest import mock

from django.test import TestCase


class TestMarkerAPI(TestCase):

    def test_url(self):
        response = self.client.get("/v1/markers/")
        self.assertEqual(response.status_code, 200)