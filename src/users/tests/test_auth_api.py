from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from users.serializers import ProfileSerializer
from users.tests.factory import ProfileFactory, UserFactory


class TestAuthAPI(TestCase):
    def setUp(self):
        self.user = UserFactory(username="user")
        self.profile = ProfileFactory(user=self.user)
        self.user.set_password("password")
        self.user.save()

    def test_login_success(self):
        """Test that the login endpoint works"""
        response = self.client.post(
            "/api/v1/auth/login/",
            {"username": self.user.username, "password": "password"},
        )
        data = response.json()
        print(data)
        assert response.status_code == 200
        assert data["access"] is not None
        assert data["user"]["pk"] == self.user.id
        assert data["user"]["username"] == self.user.username

    def test_verify_token_success(self):
        """Test that the verify token endpoint works"""
        response = self.client.post(
            "/api/v1/auth/login/", {"username": "user", "password": "password"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        token = data["access"]

        response = self.client.post("/api/v1/auth/verify/", {"token": token})
        self.assertEqual(response.status_code, 200)

    def test_verify_token_fail(self):
        """Test that verifying invalid tokens wont return 200"""

        response = self.client.post("/api/v1/auth/verify/", {"token": "invalid-token"})
        self.assertEqual(response.status_code, 401)
