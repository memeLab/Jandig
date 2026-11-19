"""
Exhibit URLs shown to users follow the host they are on (#822), always with
https:// even when the request reaches Django over plain http, because SSL
terminates at the load balancer.
"""

from django.test import TestCase
from django.urls import reverse

from core.tests.factory import ExhibitFactory
from users.tests.factory import ProfileFactory, UserFactory


class TestExhibitDetailUrl(TestCase):
    def setUp(self):
        self.exhibit = ExhibitFactory(slug="my-exhibit")

    def detail(self, host):
        response = self.client.get(
            reverse("exhibit-detail"), {"id": self.exhibit.id}, HTTP_HOST=host
        )
        assert response.status_code == 200
        return response.content.decode()

    def test_on_dev_the_url_points_to_dev(self):
        html = self.detail("dev.jandig.app")

        assert "https://dev.jandig.app/<span>my-exhibit</span>" in html

    def test_on_production_the_url_points_to_production(self):
        html = self.detail("jandig.app")

        assert "https://jandig.app/<span>my-exhibit</span>" in html

    def test_the_url_stays_https_when_the_request_arrives_over_http(self):
        # The test client sends plain http, like the load balancer does.
        html = self.detail("dev.jandig.app")

        assert "http://dev.jandig.app/" not in html

    def test_the_see_exhibition_link_stays_on_the_current_host(self):
        html = self.detail("dev.jandig.app")

        assert 'href="/my-exhibit"' in html
        assert 'href="https://jandig.app/my-exhibit"' not in html


class TestCreateExhibitUrlPreview(TestCase):
    def setUp(self):
        user = UserFactory(username="curator")
        ProfileFactory(user=user)
        self.client.force_login(user)

    def preview(self, url_name, host):
        response = self.client.get(reverse(url_name), HTTP_HOST=host)
        assert response.status_code == 200
        return response.content.decode()

    def test_ar_preview_uses_the_current_host_with_https(self):
        html = self.preview("create-ar-exhibit", "dev.jandig.app")

        assert '<label class="url-helper">https://dev.jandig.app/</label>' in html
        assert "http://dev.jandig.app/" not in html

    def test_mr_preview_uses_the_current_host_with_https(self):
        html = self.preview("create-mr-exhibit", "dev.jandig.app")

        assert '<label class="url-helper">https://dev.jandig.app/</label>' in html
        assert "http://dev.jandig.app/" not in html
