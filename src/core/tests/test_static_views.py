from django.test import TestCase
from django.urls import reverse


class TestCoreStaticViews(TestCase):
    def test_health_check(self):
        response = self.client.get(reverse("health_check"))
        assert response.status_code == 200

    def test_favicon(self):
        response = self.client.get(reverse("favicon"))
        assert response.status_code == 302
        assert response["Location"].endswith("favicon.ico")

    def test_manifest(self):
        response = self.client.get(reverse("manifest"))
        assert response.status_code == 200

    def test_service_worker(self):
        response = self.client.get(reverse("sw"))
        assert response.status_code == 200

    def test_robots_txt(self):
        response = self.client.get(reverse("robots_txt"))
        assert response.status_code == 200

    def test_mitologia_hotsite(self):
        response = self.client.get("/me/")
        assert response.status_code == 200
        response = self.client.get("/ME/")
        assert response.status_code == 200
        response = self.client.get("/me")
        assert response.status_code == 200
        response = self.client.get("/ME")
        assert response.status_code == 200
