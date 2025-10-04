from django.test import TestCase
from django.urls import reverse

from core.models import Exhibit, ExhibitTypes, Object
from core.tests.factory import ArtworkFactory, ExhibitFactory, ObjectFactory
from users.tests.factory import ProfileFactory, UserFactory


class TestCreateExhibitView(TestCase):
    def setUp(self):
        self.user = UserFactory(username="testuser")
        self.profile = ProfileFactory(user=self.user)
        self.client.force_login(self.user)
        self.artwork1 = ArtworkFactory(author=self.profile)
        self.artwork2 = ArtworkFactory(author=self.profile)
        self.object1 = ObjectFactory(author=self.profile)
        self.object2 = ObjectFactory(author=self.profile)

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
        assert response.status_code == 200
        assert (
            "That exhibit slug is already in use"
            in response.context["form"].errors["slug"][0]
        )
        assert Exhibit.objects.count() == 1  # No exhibit should be created

    def test_create_exhibit_name_already_exists(self):
        # Create an exhibit with the same name
        _ = ExhibitFactory(owner=self.profile, name="My Test Exhibit")
        assert Exhibit.objects.count() == 1  # No exhibit should be created

        url = reverse("create-exhibit")
        data = {
            "name": "My Test Exhibit",  # Same name as existing exhibit
            "slug": "other-slug",
            "artworks": f"{self.artwork1.id},{self.artwork2.id}",
        }
        response = self.client.post(url, data)
        # Should not redirect, should show form again
        assert response.status_code == 200
        assert (
            "This name is already being used"
            in response.context["form"].errors["name"][0]
        )
        assert Exhibit.objects.count() == 1  # No exhibit should be created

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
        self.assertContains(
            response,
            "Enter a valid “slug” consisting of letters, numbers, underscores or hyphens",
        )

        data["slug"] = "invalid_slug!"  # Invalid slug with special character
        response = self.client.post(url, data)
        # Should not redirect, should show form again
        assert response.status_code == 200
        assert (
            "Enter a valid “slug” consisting of letters, numbers, underscores or hyphens"
            in response.context["form"].errors["slug"][0]
        )
        assert Exhibit.objects.count() == 0  # No exhibit should be created

    def test_create_exhibit_with_artworks(self):
        url = reverse("create-exhibit")
        data = {
            "name": "My Test Exhibit",
            "slug": "my-test-exhibit",
            "artworks": f"{self.artwork1.id},{self.artwork2.id}",
        }
        response = self.client.post(url, data)
        # Should redirect to profile after creation
        assert response.status_code == 302
        # Exhibit should be created
        assert Exhibit.objects.count() == 1
        exhibit = Exhibit.objects.get(name="My Test Exhibit")
        assert exhibit.owner == self.profile
        assert exhibit.slug == "my-test-exhibit"
        self.assertSetEqual(
            set(exhibit.artworks.values_list("id", flat=True)),
            {self.artwork1.id, self.artwork2.id},
        )
        assert exhibit.exhibit_type == ExhibitTypes.AR

    def test_create_exhibit_with_objects(self):
        url = reverse("create-exhibit")
        data = {
            "name": "My Test Exhibit with Objects",
            "slug": "my-test-exhibit-objects",
            "augmenteds": f"{self.object1.id},{self.object2.id}",
        }
        response = self.client.post(url, data)
        # Should redirect to profile after creation
        assert response.status_code == 302
        # Exhibit should be created
        assert Exhibit.objects.count() == 1
        exhibit = Exhibit.objects.get(name="My Test Exhibit with Objects")
        assert exhibit.owner == self.profile
        assert exhibit.slug == "my-test-exhibit-objects"
        assert exhibit.exhibit_type == ExhibitTypes.MR
        self.assertSetEqual(
            set(exhibit.augmenteds.values_list("id", flat=True)),
            {self.object1.id, self.object2.id},
        )

    def test_create_exhibit_with_artworks_and_objects(self):
        url = reverse("create-exhibit")
        data = {
            "name": "My Test Exhibit with Artworks and Objects",
            "slug": "my-test-exhibit-art-objects",
            "artworks": f"{self.artwork1.id},{self.artwork2.id}",
            "augmenteds": f"{self.object1.id},{self.object2.id}",
        }
        response = self.client.post(url, data)
        # Should redirect to profile after creation
        assert response.status_code == 302
        # Exhibit should be created
        assert Exhibit.objects.count() == 1
        exhibit = Exhibit.objects.get(name="My Test Exhibit with Artworks and Objects")
        assert exhibit.owner == self.profile
        assert exhibit.slug == "my-test-exhibit-art-objects"
        assert exhibit.exhibit_type == ExhibitTypes.MR
        self.assertSetEqual(
            set(exhibit.artworks.values_list("id", flat=True)),
            {self.artwork1.id, self.artwork2.id},
        )
        self.assertSetEqual(
            set(exhibit.augmenteds.values_list("id", flat=True)),
            {self.object1.id, self.object2.id},
        )

    def test_create_exhibit_with_no_content(self):
        url = reverse("create-exhibit")
        data = {
            "name": "Empty Exhibit",
            "slug": "empty-exhibit",
            "artworks": "",
            "augmenteds": "",
        }
        response = self.client.post(url, data)
        # Should redirect to profile after creation
        assert response.status_code == 200
        # Exhibit should be created with no artworks or objects
        assert Exhibit.objects.count() == 0
        assert (
            "You must select at least one artwork or augmented object."
            in response.context["form"].non_field_errors()
        )


class TestEditExhibitView(TestCase):
    def setUp(self):
        self.user = UserFactory(username="edituser")
        self.profile = ProfileFactory(user=self.user)
        self.client.force_login(self.user)
        self.artwork1 = ArtworkFactory(author=self.profile)
        self.artwork2 = ArtworkFactory(author=self.profile)
        self.object1 = ObjectFactory(author=self.profile)
        self.object2 = ObjectFactory(author=self.profile)
        self.exhibit = ExhibitFactory(
            owner=self.profile,
            artworks=[self.artwork1],
            name="Edit Exhibit",
            slug="edit-exhibit",
        )

    def test_edit_exhibit_requires_login(self):
        self.client.logout()
        url = reverse("edit-exhibit", query={"id": self.exhibit.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

        # Valid request data should not be accepted without login
        data = {
            "name": "Edited Exhibit",
            "slug": "edited-exhibit",
            "artworks": f"{self.artwork1.id},{self.artwork2.id}",
            "augmenteds": f"{self.object1.id},{self.object2.id}",
        }
        response = self.client.post(url, data)
        assert response.status_code == 302
        assert reverse("login") in response.url
        # Exhibit should not be changed
        self.exhibit.refresh_from_db()
        assert self.exhibit.name == "Edit Exhibit"
        assert self.exhibit.slug == "edit-exhibit"
        self.assertSetEqual(
            set(self.exhibit.artworks.values_list("id", flat=True)),
            {self.artwork1.id},
        )

    def test_edit_exhibit_only_owner_can_edit(self):
        other_user = UserFactory(username="otheruser")
        other_profile = ProfileFactory(user=other_user)
        other_exhibit = ExhibitFactory(owner=other_profile)
        url = reverse("edit-exhibit", query={"id": other_exhibit.id})
        response = self.client.get(url)
        assert response.status_code == 404

    def test_edit_exhibit_invalid_data(self):
        url = reverse("edit-exhibit", query={"id": self.exhibit.id})
        data = {
            "name": "",
            "slug": "",
            "artworks": "",
            "augmenteds": "",
        }
        response = self.client.post(url, data)
        assert response.status_code == 200
        assert "form" in response.context
        # Exhibit should not be changed
        self.exhibit.refresh_from_db()
        assert self.exhibit.name == "Edit Exhibit"

    def test_edit_exhibit_slug_already_exists(self):
        # Create another exhibit with the same slug
        ExhibitFactory(owner=self.profile, slug="taken-slug")
        url = reverse("edit-exhibit", query={"id": self.exhibit.id})
        data = {
            "name": "New Name",
            "slug": "taken-slug",
            "artworks": str(self.artwork1.id),
        }
        response = self.client.post(url, data)
        assert response.status_code == 200
        assert (
            "That exhibit slug is already in use"
            in response.context["form"].errors["slug"][0]
        )
        self.exhibit.refresh_from_db()
        assert self.exhibit.slug != "taken-slug"

    def test_edit_exhibit_name_already_exists(self):
        ExhibitFactory(owner=self.profile, name="Taken Name")
        url = reverse("edit-exhibit", query={"id": self.exhibit.id})
        data = {
            "name": "Taken Name",
            "slug": "unique-slug",
            "artworks": str(self.artwork1.id),
        }
        response = self.client.post(url, data)
        assert response.status_code == 200
        assert (
            "This name is already being used"
            in response.context["form"].errors["name"][0]
        )
        self.exhibit.refresh_from_db()
        assert self.exhibit.name != "Taken Name"

    def test_edit_exhibit_invalid_slug(self):
        url = reverse("edit-exhibit", query={"id": self.exhibit.id})
        data = {
            "name": "Valid Name",
            "slug": "invalid slug!",
            "artworks": str(self.artwork1.id),
        }
        response = self.client.post(url, data)
        assert response.status_code == 200
        assert (
            "Enter a valid “slug” consisting of letters, numbers, underscores or hyphens."
            in response.context["form"].errors["slug"][0]
        )
        self.exhibit.refresh_from_db()
        assert self.exhibit.slug != "invalid slug!"

    def test_edit_exhibit_success(self):
        url = reverse("edit-exhibit", query={"id": self.exhibit.id})
        data = {
            "name": "Edited Exhibit",
            "slug": "edited-exhibit",
            "artworks": f"{self.artwork1.id},{self.artwork2.id}",
            "augmenteds": "",
        }
        response = self.client.post(url, data)
        assert response.status_code == 302
        self.exhibit.refresh_from_db()
        assert self.exhibit.name == "Edited Exhibit"
        assert self.exhibit.slug == "edited-exhibit"
        assert self.exhibit.exhibit_type == ExhibitTypes.AR
        self.assertSetEqual(
            set(self.exhibit.artworks.values_list("id", flat=True)),
            {self.artwork1.id, self.artwork2.id},
        )

    def test_edit_exhibit_no_changes(self):
        url = reverse("edit-exhibit", query={"id": self.exhibit.id})
        data = {
            "name": self.exhibit.name,
            "slug": self.exhibit.slug,
            "artworks": str(self.artwork1.id),
            "augmenteds": "",
        }
        response = self.client.post(url, data)
        assert response.status_code == 302
        self.exhibit.refresh_from_db()
        assert self.exhibit.name == "Edit Exhibit"
        assert self.exhibit.slug == "edit-exhibit"
        assert self.exhibit.exhibit_type == ExhibitTypes.AR

        self.assertSetEqual(
            set(self.exhibit.artworks.values_list("id", flat=True)),
            {self.artwork1.id},
        )

    def test_edit_exhibit_with_objects(self):
        url = reverse("edit-exhibit", query={"id": self.exhibit.id})
        data = {
            "name": "Edited Exhibit with Objects",
            "slug": "edited-exhibit-objects",
            "artworks": str(self.artwork1.id),
            "augmenteds": f"{self.object1.id},{self.object2.id}",
        }
        response = self.client.post(url, data)
        assert response.status_code == 302
        self.exhibit.refresh_from_db()
        assert self.exhibit.name == "Edited Exhibit with Objects"
        assert self.exhibit.slug == "edited-exhibit-objects"
        assert self.exhibit.exhibit_type == ExhibitTypes.MR
        self.assertSetEqual(
            set(self.exhibit.artworks.values_list("id", flat=True)),
            {self.artwork1.id},
        )
        self.assertSetEqual(
            set(self.exhibit.augmenteds.values_list("id", flat=True)),
            {self.object1.id, self.object2.id},
        )

    def test_edit_exhibit_type_changes_correctly(self):
        # Initially, the exhibit has artworks only
        url = reverse("edit-exhibit", query={"id": self.exhibit.id})
        data = {
            "name": "Exhibit with Artworks",
            "slug": "exhibit-with-artworks",
            "artworks": f"{self.artwork1.id},{self.artwork2.id}",
            "augmenteds": "",
        }
        response = self.client.post(url, data)
        assert response.status_code == 302
        self.exhibit.refresh_from_db()
        assert self.exhibit.exhibit_type == ExhibitTypes.AR

        # Now add objects to change it to MR
        data["augmenteds"] = f"{self.object1.id},{self.object2.id}"
        response = self.client.post(url, data)
        assert response.status_code == 302
        self.exhibit.refresh_from_db()
        assert self.exhibit.exhibit_type == ExhibitTypes.MR

        data["artworks"] = ""
        response = self.client.post(url, data)
        assert response.status_code == 302
        self.exhibit.refresh_from_db()
        assert self.exhibit.exhibit_type == ExhibitTypes.MR  # Should remain MR even

        data["augmenteds"] = ""
        data["artworks"] = f"{self.artwork1.id},{self.artwork2.id}"
        response = self.client.post(url, data)
        assert response.status_code == 302
        self.exhibit.refresh_from_db()
        assert self.exhibit.exhibit_type == ExhibitTypes.AR  # Should change back to AR

    def test_edit_exhibit_comes_filled_with_current_data(self):
        self.exhibit.artworks.set([self.artwork1, self.artwork2])
        self.exhibit.augmenteds.set([self.object1, self.object2])

        url = reverse("edit-exhibit", query={"id": self.exhibit.id})
        response = self.client.get(url)
        assert response.status_code == 200
        assert response.context["form"].initial["name"] == self.exhibit.name
        assert response.context["form"].initial["slug"] == self.exhibit.slug
        assert "objects" in response.context
        assert "artworks" in response.context
        assert list(response.context["artworks"]) == [self.artwork2, self.artwork1]
        assert list(response.context["objects"]) == list(
            Object.objects.all().order_by("-created")
        )
        assert response.context["selected_artworks"] == "".join(
            f"{artwork.id}," for artwork in self.exhibit.artworks.all()
        ).rstrip(",")
        assert response.context["selected_objects"] == "".join(
            f"{object.id}," for object in self.exhibit.augmenteds.all()
        ).rstrip(",")
