from django.test import TestCase
from django.urls import reverse

from core.models import Exhibit
from core.tests.factory import ArtworkFactory, ExhibitFactory
from users.tests.factory import ProfileFactory, UserFactory


class TestCreateExhibitView(TestCase):
    def setUp(self):
        self.user = UserFactory(username="testuser")
        self.profile = ProfileFactory(user=self.user)
        self.client.force_login(self.user)
        self.artwork1 = ArtworkFactory(author=self.profile)
        self.artwork2 = ArtworkFactory(author=self.profile)

    def test_create_exhibit_requires_login(self):
        self.client.logout()
        url = reverse("create-exhibit")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Should redirect to login
        self.assertRedirects(response, f"{reverse('login')}?next={url}")

        # Valid request data should not be accepted without login
        data = {
            "name": "My Test Exhibit",
            "slug": "my-test-exhibit",
            "artworks": f"{self.artwork1.id},{self.artwork2.id}",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_create_exhibit_invalid_data(self):
        url = reverse("create-exhibit")
        data = {
            "name": "",  # Missing name
            "slug": "",
            "artworks": "",
        }
        response = self.client.post(url, data)
        # Should not redirect, should show form again
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form")
        self.assertEqual(Exhibit.objects.count(), 0)  # No exhibit should be created

    def test_create_exhibit_slug_already_exists(self):
        # Create an exhibit with the same slug
        _ = ExhibitFactory(owner=self.profile, slug="my-test-exhibit")
        self.assertEqual(Exhibit.objects.count(), 1)  # No exhibit should be created

        url = reverse("create-exhibit")
        data = {
            "name": "My Test Exhibit",
            "slug": "my-test-exhibit",  # Same slug as existing exhibit
            "artworks": f"{self.artwork1.id},{self.artwork2.id}",
        }
        response = self.client.post(url, data)
        # Should not redirect, should show form again
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "That exhibit slug is already in use")
        self.assertEqual(Exhibit.objects.count(), 1)  # No exhibit should be created

    def test_create_exhibit_name_already_exists(self):
        # Create an exhibit with the same name
        _ = ExhibitFactory(owner=self.profile, name="My Test Exhibit")
        self.assertEqual(Exhibit.objects.count(), 1)  # No exhibit should be created

        url = reverse("create-exhibit")
        data = {
            "name": "My Test Exhibit",  # Same name as existing exhibit
            "slug": "other-slug",
            "artworks": f"{self.artwork1.id},{self.artwork2.id}",
        }
        response = self.client.post(url, data)
        # Should not redirect, should show form again
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This name is already being used")
        self.assertEqual(Exhibit.objects.count(), 1)  # No exhibit should be created

    def test_create_exhibit_invalid_slug(self):
        url = reverse("create-exhibit")
        data = {
            "name": "My Test Exhibit",
            "slug": "invalid slug",  # Invalid slug with spaces
            "artworks": f"{self.artwork1.id},{self.artwork2.id}",
        }
        response = self.client.post(url, data)
        # Should not redirect, should show form again
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "contain spaces or special characters")

        data["slug"] = "invalid_slug!"  # Invalid slug with special character
        response = self.client.post(url, data)
        # Should not redirect, should show form again
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "contain spaces or special characters")
        self.assertEqual(Exhibit.objects.count(), 0)  # No exhibit should be created

    def test_create_exhibit_success(self):
        url = reverse("create-exhibit")
        data = {
            "name": "My Test Exhibit",
            "slug": "my-test-exhibit",
            "artworks": f"{self.artwork1.id},{self.artwork2.id}",
        }
        response = self.client.post(url, data)
        # Should redirect to profile after creation
        self.assertEqual(response.status_code, 302)
        # Exhibit should be created
        self.assertEqual(Exhibit.objects.count(), 1)
        exhibit = Exhibit.objects.get(name="My Test Exhibit")
        self.assertEqual(exhibit.owner, self.profile)
        self.assertEqual(exhibit.slug, "my-test-exhibit")
        self.assertSetEqual(
            set(exhibit.artworks.values_list("id", flat=True)),
            {self.artwork1.id, self.artwork2.id},
        )


class TestEditExhibitView(TestCase):
    def setUp(self):
        self.user = UserFactory(username="edituser")
        self.profile = ProfileFactory(user=self.user)
        self.client.force_login(self.user)
        self.artwork1 = ArtworkFactory(author=self.profile)
        self.artwork2 = ArtworkFactory(author=self.profile)
        self.exhibit = ExhibitFactory(
            owner=self.profile,
            artworks=[self.artwork1],
            name="Edit Exhibit",
            slug="edit-exhibit",
        )

    def test_edit_exhibit_requires_login(self):
        self.client.logout()
        url = reverse("edit-exhibit") + f"?id={self.exhibit.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

        # Valid request data should not be accepted without login
        data = {
            "name": "Edited Exhibit",
            "slug": "edited-exhibit",
            "artworks": f"{self.artwork1.id},{self.artwork2.id}",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)
        # Exhibit should not be changed
        self.exhibit.refresh_from_db()
        self.assertEqual(self.exhibit.name, "Edit Exhibit")
        self.assertEqual(self.exhibit.slug, "edit-exhibit")
        self.assertSetEqual(
            set(self.exhibit.artworks.values_list("id", flat=True)),
            {self.artwork1.id},
        )

    def test_edit_exhibit_only_owner_can_edit(self):
        other_user = UserFactory(username="otheruser")
        other_profile = ProfileFactory(user=other_user)
        other_exhibit = ExhibitFactory(owner=other_profile)
        url = reverse("edit-exhibit") + f"?id={other_exhibit.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_edit_exhibit_invalid_data(self):
        url = reverse("edit-exhibit") + f"?id={self.exhibit.id}"
        data = {
            "name": "",
            "slug": "",
            "artworks": "",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form")
        # Exhibit should not be changed
        self.exhibit.refresh_from_db()
        self.assertEqual(self.exhibit.name, "Edit Exhibit")

    def test_edit_exhibit_slug_already_exists(self):
        # Create another exhibit with the same slug
        ExhibitFactory(owner=self.profile, slug="taken-slug")
        url = reverse("edit-exhibit") + f"?id={self.exhibit.id}"
        data = {
            "name": "New Name",
            "slug": "taken-slug",
            "artworks": str(self.artwork1.id),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "That exhibit slug is already in use")
        self.exhibit.refresh_from_db()
        self.assertNotEqual(self.exhibit.slug, "taken-slug")

    def test_edit_exhibit_name_already_exists(self):
        ExhibitFactory(owner=self.profile, name="Taken Name")
        url = reverse("edit-exhibit") + f"?id={self.exhibit.id}"
        data = {
            "name": "Taken Name",
            "slug": "unique-slug",
            "artworks": str(self.artwork1.id),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This name is already being used")
        self.exhibit.refresh_from_db()
        self.assertNotEqual(self.exhibit.name, "Taken Name")

    def test_edit_exhibit_invalid_slug(self):
        url = reverse("edit-exhibit") + f"?id={self.exhibit.id}"
        data = {
            "name": "Valid Name",
            "slug": "invalid slug!",
            "artworks": str(self.artwork1.id),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "contain spaces or special characters")
        self.exhibit.refresh_from_db()
        self.assertNotEqual(self.exhibit.slug, "invalid slug!")

    def test_edit_exhibit_success(self):
        url = reverse("edit-exhibit") + f"?id={self.exhibit.id}"
        data = {
            "name": "Edited Exhibit",
            "slug": "edited-exhibit",
            "artworks": f"{self.artwork1.id},{self.artwork2.id}",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.exhibit.refresh_from_db()
        self.assertEqual(self.exhibit.name, "Edited Exhibit")
        self.assertEqual(self.exhibit.slug, "edited-exhibit")
        self.assertSetEqual(
            set(self.exhibit.artworks.values_list("id", flat=True)),
            {self.artwork1.id, self.artwork2.id},
        )

    def test_edit_exhibit_no_changes(self):
        url = reverse("edit-exhibit") + f"?id={self.exhibit.id}"
        data = {
            "name": self.exhibit.name,
            "slug": self.exhibit.slug,
            "artworks": str(self.artwork1.id),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.exhibit.refresh_from_db()
        self.assertEqual(self.exhibit.name, "Edit Exhibit")
        self.assertEqual(self.exhibit.slug, "edit-exhibit")
        self.assertSetEqual(
            set(self.exhibit.artworks.values_list("id", flat=True)),
            {self.artwork1.id},
        )
