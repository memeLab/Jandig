from django.test import TestCase
from django.urls import reverse


class TestClipping(TestCase):
    def test_clippings_work(self):
        """
        Test the clipping page
        """
        response = self.client.get(reverse("clipping"))

        assert response.status_code == 200
        assert (
            response.context["clippings"].count() == 13
        )  # We have 13 clipping on a data migration
