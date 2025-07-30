from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from core.tests.factory import MarkerFactory, ObjectFactory


class TestHTMXGetElements(TestCase):
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.profile = self.user.profile

        # Create test markers
        self.markers = []
        for i in range(15):  # Create more than MODAL_PAGE_SIZE to test pagination
            marker = MarkerFactory.create(title=f"Test Marker {i}", owner=self.profile)
            self.markers.append(marker)

        # Create test objects
        self.objects = []
        for i in range(12):  # Create more than MODAL_PAGE_SIZE to test pagination
            obj = ObjectFactory.create(title=f"Test Object {i}", owner=self.profile)
            self.objects.append(obj)

    def test_unauthenticated_request_does_not_work(self):
        """Test that unauthenticated users get 302 to login"""
        response = self.client.get(
            reverse("get-element"),
            {"element_type": "marker", "page": "1"},
            HTTP_HX_REQUEST="true",
        )
        # redirects to login page
        self.assertEqual(response.status_code, 302)

    def test_non_htmx_request_returns_404(self):
        """Test that non-HTMX requests get 404"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(
            reverse("get-element"), {"element_type": "marker", "page": "1"}
        )
        self.assertEqual(response.status_code, 404)

    def test_valid_marker_request(self):
        """Test valid marker request returns correct data"""
        self.client.login(username="testuser", password="testpass123")

        with patch.object(settings, "MODAL_PAGE_SIZE", 10):
            response = self.client.get(
                reverse("get-element"),
                {"element_type": "marker", "page": "1"},
                HTTP_HX_REQUEST="true",
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Marker")
        self.assertIn("repository_list", response.context)
        self.assertEqual(response.context["element_type"], "marker")
        self.assertEqual(response.context["htmx"], "false")

    def test_valid_object_request(self):
        """Test valid object request returns correct data"""
        self.client.login(username="testuser", password="testpass123")

        with patch.object(settings, "MODAL_PAGE_SIZE", 10):
            response = self.client.get(
                reverse("get-element"),
                {"element_type": "object", "page": "1"},
                HTTP_HX_REQUEST="true",
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Object")
        self.assertIn("repository_list", response.context)
        self.assertEqual(response.context["element_type"], "object")

    def test_invalid_element_type_raises_error(self):
        """Test that invalid element type raises 404"""
        self.client.login(username="testuser", password="testpass123")

        response = self.client.get(
            reverse("get-element"),
            {"element_type": "invalid", "page": "1"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 404)

    def test_marker_pagination_first_page(self):
        """Test marker pagination on first page"""
        self.client.login(username="testuser", password="testpass123")

        with patch.object(settings, "MODAL_PAGE_SIZE", 5):
            response = self.client.get(
                reverse("get-element"),
                {"element_type": "marker", "page": "1"},
                HTTP_HX_REQUEST="true",
            )

        self.assertEqual(response.status_code, 200)
        repository_list = response.context["repository_list"]
        self.assertEqual(len(repository_list), 5)
        self.assertEqual(repository_list.number, 1)

    def test_marker_pagination_second_page(self):
        """Test marker pagination on second page"""
        self.client.login(username="testuser", password="testpass123")

        with patch.object(settings, "MODAL_PAGE_SIZE", 5):
            response = self.client.get(
                reverse("get-element"),
                {"element_type": "marker", "page": "2"},
                HTTP_HX_REQUEST="true",
            )

        self.assertEqual(response.status_code, 200)
        repository_list = response.context["repository_list"]
        self.assertEqual(len(repository_list), 5)
        self.assertEqual(repository_list.number, 2)

    def test_object_pagination_first_page(self):
        """Test object pagination on first page"""
        self.client.login(username="testuser", password="testpass123")

        with patch.object(settings, "MODAL_PAGE_SIZE", 8):
            response = self.client.get(
                reverse("get-element"),
                {"element_type": "object", "page": "1"},
                HTTP_HX_REQUEST="true",
            )

        self.assertEqual(response.status_code, 200)
        repository_list = response.context["repository_list"]
        self.assertEqual(len(repository_list), 8)
        self.assertEqual(repository_list.number, 1)

    def test_page_beyond_range_returns_last_page(self):
        """Test that requesting page beyond range returns last page"""
        self.client.login(username="testuser", password="testpass123")

        with patch.object(settings, "MODAL_PAGE_SIZE", 5):
            response = self.client.get(
                reverse("get-element"),
                {"element_type": "marker", "page": "999"},
                HTTP_HX_REQUEST="true",
            )

        self.assertEqual(response.status_code, 200)
        repository_list = response.context["repository_list"]
        # Should return the last page (page 3 with 15 items and page size 5)
        self.assertEqual(repository_list.number, 3)

    def test_default_page_parameter(self):
        """Test that missing page parameter defaults to 1"""
        self.client.login(username="testuser", password="testpass123")

        response = self.client.get(
            reverse("get-element"), {"element_type": "marker"}, HTTP_HX_REQUEST="true"
        )

        self.assertEqual(response.status_code, 200)
        repository_list = response.context["repository_list"]
        self.assertEqual(repository_list.number, 1)

    def test_markers_ordered_by_created_desc(self):
        """Test that markers are ordered by creation date descending"""
        self.client.login(username="testuser", password="testpass123")

        with patch.object(settings, "MODAL_PAGE_SIZE", 15):
            response = self.client.get(
                reverse("get-element"),
                {"element_type": "marker", "page": "1"},
                HTTP_HX_REQUEST="true",
            )

        self.assertEqual(response.status_code, 200)
        repository_list = response.context["repository_list"]

        # Check that items are in descending order by creation
        for i in range(len(repository_list) - 1):
            self.assertGreaterEqual(
                repository_list[i].created, repository_list[i + 1].created
            )

    def test_objects_ordered_by_created_desc(self):
        """Test that objects are ordered by creation date descending"""
        self.client.login(username="testuser", password="testpass123")

        with patch.object(settings, "MODAL_PAGE_SIZE", 12):
            response = self.client.get(
                reverse("get-element"),
                {"element_type": "object", "page": "1"},
                HTTP_HX_REQUEST="true",
            )

        self.assertEqual(response.status_code, 200)
        repository_list = response.context["repository_list"]

        # Check that items are in descending order by creation
        for i in range(len(repository_list) - 1):
            self.assertGreaterEqual(
                repository_list[i].created, repository_list[i + 1].created
            )
