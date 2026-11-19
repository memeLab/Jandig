from django.test import TestCase
from django.urls import reverse

from users.models import Profile, User


class TestPublicProfile(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="artista", password="secret")
        self.other = User.objects.create_user(username="visitante", password="secret")

    def url(self, username="artista"):
        return reverse("public-profile", kwargs={"username": username})

    def test_anyone_can_see_a_user_profile_without_logging_in(self):
        response = self.client.get(self.url())

        assert response.status_code == 200

    def test_unknown_username_returns_404(self):
        response = self.client.get(self.url("nobody-here"))

        assert response.status_code == 404

    def test_a_visitor_gets_no_edit_or_delete_controls(self):
        self.client.login(username="visitante", password="secret")
        response = self.client.get(self.url())

        assert response.context["is_owner"] is False

    def test_the_owner_viewing_their_own_public_page_keeps_the_controls(self):
        self.client.login(username="artista", password="secret")
        response = self.client.get(self.url())

        assert response.context["is_owner"] is True

    def test_the_page_does_not_expose_the_email_address(self):
        self.owner.email = "private@example.com"
        self.owner.save()

        response = self.client.get(self.url())

        assert b"private@example.com" not in response.content

    def test_the_profile_in_context_is_the_requested_user(self):
        response = self.client.get(self.url())

        assert response.context["profile"] == Profile.objects.get(user=self.owner)

    def test_literal_routes_still_win_over_the_username_route(self):
        self.client.login(username="artista", password="secret")

        response = self.client.get(reverse("profile"))

        assert response.status_code == 200
        assert response.context["is_owner"] is True


class TestProfileLinksAreDefensive(TestCase):
    """A username can be empty in existing data; the link must not 500."""

    def test_marker_modal_renders_when_the_owner_has_no_username(self):
        from core.tests.factory import MarkerFactory

        marker = MarkerFactory()
        marker.owner.user.username = ""
        marker.owner.user.save()

        response = self.client.get(f"/api/v1/markers/{marker.pk}/?format=modal")

        assert response.status_code == 200
