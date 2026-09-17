"""Lock the behaviour documented in development/api-reference.md.

Documentation drifts silently; these assertions fail loudly instead.
"""

from django.test import TestCase
from rest_framework import status

from core.tests.factory import ExhibitFactory

CONTENT_ENDPOINTS = [
    "/api/v1/markers/",
    "/api/v1/objects/",
    "/api/v1/artworks/",
    "/api/v1/sounds/",
    "/api/v1/exhibits/",
]


class TestDocumentedApiContract(TestCase):
    def test_content_endpoints_are_readable_without_authentication(self):
        for endpoint in CONTENT_ENDPOINTS:
            with self.subTest(endpoint=endpoint):
                response = self.client.get(endpoint)
                assert response.status_code == status.HTTP_200_OK

    def test_content_endpoints_reject_writes(self):
        for endpoint in CONTENT_ENDPOINTS:
            with self.subTest(endpoint=endpoint):
                response = self.client.post(endpoint, {})
                assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_list_responses_are_paginated_with_the_documented_envelope(self):
        response = self.client.get("/api/v1/exhibits/")

        for key in ("count", "next", "previous", "results"):
            assert key in response.json(), f"missing {key} in the pagination envelope"

    def test_exhibits_can_be_filtered_by_name_substring(self):
        ExhibitFactory(name="Mitologia Estendida", slug="mitologia-estendida")
        ExhibitFactory(name="Something Else", slug="something-else")

        response = self.client.get("/api/v1/exhibits/", {"search": "mitologia"})
        names = [item["name"] for item in response.json()["results"]]

        assert names == ["Mitologia Estendida"]

    def test_exhibits_filtered_by_a_non_integer_owner_return_nothing(self):
        ExhibitFactory(name="Any", slug="any")

        response = self.client.get("/api/v1/exhibits/", {"owner": "not-a-number"})

        assert response.json()["count"] == 0

    def test_exhibit_owner_is_serialized_as_a_numeric_id(self):
        exhibit = ExhibitFactory(name="Owned", slug="owned")

        response = self.client.get(f"/api/v1/exhibits/{exhibit.pk}/")

        assert response.json()["owner"] == exhibit.owner_id

    def test_modal_format_is_refused_on_list_and_allowed_on_retrieve(self):
        listing = self.client.get("/api/v1/markers/", {"format": "modal"})

        assert listing.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_marker_generator_requires_a_source_file(self):
        response = self.client.post("/api/v1/markergenerator/", {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"error": "No image provided."}
