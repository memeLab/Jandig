"""Test using the object API for Jandig Objects"""

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import Count
from django.test import TestCase

from core.models import Object
from core.serializers import ObjectSerializer
from users.models import User

fake_file = SimpleUploadedFile("fake_file.png", b"these are the file contents!")


class TestObjectAPI(TestCase):
    def setUp(self):
        self.user = User.objects.create()
        self.profile = self.user.profile

    def test_url(self):
        response = self.client.get("/api/v1/objects/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 0)
        self.assertEqual(data["next"], None)
        self.assertEqual(data["previous"], None)
        self.assertEqual(data["results"], [])

    def test_api_objects_lists_one_object(self):
        # Create an object
        obj = Object.objects.create(owner=self.profile, source=fake_file)

        # Annotate the object to include the exhibit count
        annotated_obj = Object.objects.annotate(
            exhibits_count=Count("artworks__exhibits", distinct=True)
        ).get(id=obj.id)

        response = self.client.get("/api/v1/objects/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["next"], None)
        self.assertEqual(data["previous"], None)
        first_result = data["results"][0]
        serializer_data = ObjectSerializer(annotated_obj).data
        # Asserts the serializer is being used by the endpoint
        assert first_result == serializer_data

        # Asserts the serializer uses all the needed fields
        self.assertIn("id", first_result)
        self.assertIn("owner", first_result)
        self.assertIn("source", first_result)
        self.assertIn("uploaded_at", first_result)
        self.assertIn("author", first_result)
        self.assertIn("title", first_result)
        self.assertIn("scale", first_result)
        self.assertIn("position", first_result)
        self.assertIn("rotation", first_result)
        self.assertIn("artworks_count", first_result)
        self.assertIn("exhibits_count", first_result)

    def test_api_objects_lists_multiple_objects(self):
        for _ in range(0, settings.PAGE_SIZE + 1):
            Object.objects.create(owner=self.profile, source=fake_file)

        response = self.client.get("/api/v1/objects/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], settings.PAGE_SIZE + 1)
        self.assertEqual(
            data["next"],
            f"http://testserver/api/v1/objects/?limit={settings.PAGE_SIZE}&offset={settings.PAGE_SIZE}",
        )
        self.assertEqual(data["previous"], None)
        self.assertEqual(len(data["results"]), 20)

    def test_retrieve_object(self):
        # Create an object
        obj = Object.objects.create(owner=self.profile, source=fake_file)

        # Annotate the object to include the exhibit count
        annotated_obj = Object.objects.annotate(
            exhibits_count=Count("artworks__exhibits", distinct=True)
        ).get(id=obj.id)

        response = self.client.get(f"/api/v1/objects/{obj.id}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        serializer_data = ObjectSerializer(annotated_obj).data
        # Asserts the serializer is being used by the endpoint
        assert data == serializer_data
