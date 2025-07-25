"""Test using the marker API for Jandig Markers"""

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import Count
from django.test import TestCase

from core.models import Marker
from core.serializers import MarkerSerializer
from core.tests.factory import MarkerFactory
from users.models import User

fake_file = SimpleUploadedFile("fake_file.png", b"these are the file contents!")


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
        # Create a marker
        marker = Marker.objects.create(owner=self.profile, source=fake_file)
        # Annotate the marker to include the exhibit count
        annotated_marker = Marker.objects.annotate(
            exhibits_count=Count("artworks__exhibits", distinct=True)
        ).get(id=marker.id)

        response = self.client.get("/api/v1/markers/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["next"], None)
        self.assertEqual(data["previous"], None)
        first_result = data["results"][0]
        serializer_data = MarkerSerializer(annotated_marker).data
        # Asserts the serializer is being used by the endpoint
        assert first_result == serializer_data

        # Asserts the serializer uses all the needed fields
        self.assertIn("id", first_result)
        self.assertIn("owner", first_result)
        self.assertIn("source", first_result)
        self.assertIn("created", first_result)
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
            f"http://testserver/api/v1/markers/?limit={settings.PAGE_SIZE}&offset=20",
        )
        self.assertEqual(data["previous"], None)
        self.assertEqual(len(data["results"]), 20)

    def test_retrieve_marker(self):
        # Create a marker
        marker = Marker.objects.create(owner=self.profile, source=fake_file)
        # Annotate the marker to include the exhibit count
        annotated_marker = Marker.objects.annotate(
            exhibits_count=Count("artworks__exhibits", distinct=True)
        ).get(id=marker.id)

        response = self.client.get(f"/api/v1/markers/{marker.id}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        serializer_data = MarkerSerializer(annotated_marker).data
        # Asserts the serializer is being used by the endpoint
        assert data == serializer_data

    def test_retrieve_marker_as_modal(self):
        # Create a marker
        marker = MarkerFactory.create(owner=self.profile, source=fake_file)
        # Annotate the marker to include the exhibit count
        annotated_marker = Marker.objects.annotate(
            exhibits_count=Count("artworks__exhibits", distinct=True)
        ).get(id=marker.id)
        response = self.client.get(f"/api/v1/markers/{marker.id}/?format=modal")
        self.assertEqual(response.status_code, 200)
        html = response.content.decode("utf-8")

        assert annotated_marker.title in html
        assert annotated_marker.source.url in html
        assert annotated_marker.created.strftime("%d/%m/%Y") in html
        assert annotated_marker.author in html
        assert annotated_marker.owner.user.username in html
        assert str(annotated_marker.file_size) in html
        assert annotated_marker.used_in_html_string() in html

    def test_retrieve_marker_as_modal_with_go_back_button(self):
        # Create a marker
        marker = MarkerFactory.create(owner=self.profile, source=fake_file)
        # Annotate the marker to include the exhibit count
        annotated_marker = Marker.objects.annotate(
            exhibits_count=Count("artworks__exhibits", distinct=True)
        ).get(id=marker.id)

        go_back_url = "/api/v1/artworks/1/?format=modal"
        response = self.client.get(
            f"/api/v1/markers/{marker.id}/?format=modal&go_back_url={go_back_url}"
        )
        self.assertEqual(response.status_code, 200)
        html = response.content.decode("utf-8")

        assert annotated_marker.title in html
        assert annotated_marker.source.url in html
        assert annotated_marker.created.strftime("%d/%m/%Y") in html
        assert annotated_marker.author in html
        assert annotated_marker.owner.user.username in html
        assert str(annotated_marker.file_size) in html
        assert annotated_marker.used_in_html_string() in html
        assert go_back_url in html
