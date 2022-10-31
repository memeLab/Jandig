"""Test using the marker API for Jandig Markers"""

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from core.models import Marker
from users.models import User

fake_file = SimpleUploadedFile("fake_file.png", b"these are the file contents!")


class TestMarkerAPI(TestCase):
    def setUp(self):
        user = User.objects.create()
        marker = Marker.objects.create(owner=user.profile, source=fake_file)

    def test_url(self):
        response = self.client.get("/v1/markers/")
        self.assertEqual(response.status_code, 200)
