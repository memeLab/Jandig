"""Tests for the Jandig Profiles API"""

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from users.serializers import ProfileSerializer
from users.tests.factory import ProfileFactory, UserFactory


class TestProfileAPI(TestCase):
    def test_url(self):
        """Test that the root page of the api exists"""
        response = self.client.get("/api/v1/profiles/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 0)
        self.assertEqual(data["next"], None)
        self.assertEqual(data["previous"], None)
        self.assertEqual(data["results"], [])

    def test_api_profiles_lists_one_profile(self):
        """API returns one profile if there is one profile"""
        user = UserFactory(username="testuserprofile")
        profile = ProfileFactory(user=user)
        response = self.client.get("/api/v1/profiles/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["id"] == profile.id
        assert data["results"][0]["user_id"] == profile.user.id
        assert data["results"][0]["username"] == profile.user.username
        assert data["results"] == ProfileSerializer([profile], many=True).data

    def test_api_profiles_lists_multiple_profiles(self):
        """API returns multiple profiles if there are multiple profiles"""
        for i in range(0, settings.PAGE_SIZE + 1):
            ProfileFactory(user=UserFactory(username=f"user_{i}"))
        response = self.client.get("/api/v1/profiles/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], settings.PAGE_SIZE + 1)
        self.assertEqual(
            data["next"],
            f"http://testserver/api/v1/profiles/?limit={settings.PAGE_SIZE}&offset={settings.PAGE_SIZE}",
        )

    def test_retrieve_profile_by_id(self):
        """API returns one profile if there is one profile"""
        user = UserFactory(username="testuserprofile")
        profile = ProfileFactory(user=user)
        response = self.client.get(f"/api/v1/profiles/{profile.id}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        assert data["id"] == profile.id
        assert data["user_id"] == profile.user.id
        assert data["username"] == profile.user.username
        assert data == ProfileSerializer(profile).data

    def test_search_by_user_id(self):
        """API returns one profile if there is one profile"""
        user = UserFactory(username="testuserprofile")
        profile = ProfileFactory(user=user)
        response = self.client.get(f"/api/v1/profiles/?user={profile.user.id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["id"] == profile.id
        assert data["results"][0]["user_id"] == profile.user.id
        assert data["results"][0]["username"] == profile.user.username

    def test_search_by_invalid_ids(self):
        """API doens't fail with invalid user ids"""
        response = self.client.get(f"/api/v1/profiles/?user=99999")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        assert data["count"] == 0
        assert data["results"] == []

        response = self.client.get(f"/api/v1/profiles/?user=invalid")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        assert data["count"] == 0
        assert data["results"] == []

        response = self.client.get(f"/api/v1/profiles/?user=")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        assert data["count"] == 0
        assert data["results"] == []
