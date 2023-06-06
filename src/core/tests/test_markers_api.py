"""Test using the marker API for Jandig Markers"""

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from core.models import Marker
from core.serializers.markers import MarkerSerializer
from users.models import User

fake_file = SimpleUploadedFile(
    "fake_file.png",
    b"these are the file contents!"
)


class TestMarkerAPI(TestCase):
    def setUp(self):
        self.user = User.objects.create()
        self.profile = self.user.profile

    def test_url(self):
        response = self.client.get("/api/v1/markers/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 0)
        self.assertEqual(data["next"], None)
        self.assertEqual(data["previous"], None)
        self.assertEqual(data["results"], [])

    def test_api_markers_lists_one_marker(self):
        marker = Marker.objects.create(owner=self.profile, source=fake_file)
        response = self.client.get("/api/v1/markers/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["next"], None)
        self.assertEqual(data["previous"], None)
        first_result = data["results"][0]
        serializer_data = MarkerSerializer(marker).data
        serializer_data["source"] = "http://testserver" + serializer_data[
            "source"
        ]
        # Asserts the serializer is being used by the endpoint
        self.assertDictEqual(first_result, serializer_data)

        # Asserts the serializer uses all the needed fields
        self.assertIn("id", first_result)
        self.assertIn("owner", first_result)
        self.assertIn("source", first_result)
        self.assertIn("uploaded_at", first_result)
        self.assertIn("author", first_result)
        self.assertIn("title", first_result)
        self.assertIn("patt", first_result)

    def test_api_markers_lists_multiple_markers(self):
        for _ in range(0, settings.PAGE_SIZE + 1):
            Marker.objects.create(owner=self.profile, source=fake_file)

        response = self.client.get("/api/v1/markers/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], settings.PAGE_SIZE + 1)
        self.assertEqual(
            data["next"],
            test_server_url,
        )
        self.assertEqual(data["previous"], None)
        self.assertEqual(len(data["results"]), 20)

    def test_retrieve_marker(self):
        marker = Marker.objects.create(owner=self.profile, source=fake_file)
        response = self.client.get("/api/v1/markers/1/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        serializer_data = MarkerSerializer(marker).data
        serializer_data["source"] = "http://testserver" + serializer_data[
            "source"
        ]
        # Asserts the serializer is being used by the endpoint
        self.assertDictEqual(data, serializer_data)
