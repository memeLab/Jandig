import base64
import json

from django.test import TestCase

from users.tests.factory import ProfileFactory, UserFactory


class TestAuthAPI(TestCase):
    def setUp(self):
        self.user = UserFactory(username="user")
        self.profile = ProfileFactory(user=self.user)
        self.user.set_password("password")
        self.user.save()

    def test_login_with_username_success(self):
        """Test that the login endpoint works"""
        response = self.client.post(
            "/api/v1/auth/login/",
            {"username": self.user.username, "password": "password"},
        )
        data = response.json()
        assert response.status_code == 200
        assert data["access"] is not None
        assert data["refresh"] is not None
        # Access JWT token payload
        payload = data["access"].split(".")[1]
        # Decode the base 64 payload
        decoded_payload = base64.b64decode(payload + "==").decode("utf-8")
        json_payload = json.loads(decoded_payload)

        # Check the payload contains the user id
        assert int(json_payload["user_profile_id"]) == self.user.profile.id
        assert int(json_payload["user_id"]) == self.user.id
        assert json_payload["username"] == self.user.username

    def test_login_with_email_success(self):
        """Test that the login endpoint works"""
        response = self.client.post(
            "/api/v1/auth/login/",
            {"username": self.user.email, "password": "password"},
        )
        data = response.json()
        assert response.status_code == 200
        assert data["access"] is not None
        assert data["refresh"] is not None
        # Access JWT token payload
        payload = data["access"].split(".")[1]
        # Decode the base 64 payload
        decoded_payload = base64.b64decode(payload + "==").decode("utf-8")
        json_payload = json.loads(decoded_payload)

        # Check the payload contains the user id
        assert int(json_payload["user_profile_id"]) == self.user.profile.id
        assert int(json_payload["user_id"]) == self.user.id
        assert json_payload["username"] == self.user.username

    def test_login_fails_with_wrong_user(self):
        """Test that the login endpoint fails with wrong credentials"""
        response = self.client.post(
            "/api/v1/auth/login/", {"username": "not_user", "password": "password"}
        )
        self.assertEqual(response.status_code, 401)

    def test_login_fails_with_wrong_password(self):
        """Test that the login endpoint fails with wrong credentials"""
        response = self.client.post(
            "/api/v1/auth/login/", {"username": "user", "password": "wrong_password"}
        )
        self.assertEqual(response.status_code, 401)

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

    def test_refresh_token_success(self):
        """Test that the refresh token endpoint works"""
        response = self.client.post(
            "/api/v1/auth/login/", {"username": "user", "password": "password"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        assert data["refresh"] is not None
        assert data["access"] is not None
        old_access_token = data["access"]
        refresh_token = data["refresh"]

        response = self.client.post("/api/v1/auth/verify/", {"token": old_access_token})
        self.assertEqual(response.status_code, 200)

        response = self.client.post("/api/v1/auth/refresh/", {"refresh": refresh_token})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        assert data["access"] is not None
        access_token = data["access"]
        assert access_token != old_access_token

        response = self.client.post("/api/v1/auth/verify/", {"token": access_token})
        self.assertEqual(response.status_code, 200)
