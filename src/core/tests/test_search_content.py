from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from core.models import Artwork, Exhibit, ExhibitTypes
from core.tests.factory import (
    ArtworkFactory,
    ExhibitFactory,
    MarkerFactory,
    ObjectFactory,
    SoundFactory,
)
from core.tests.utils import get_example_object
from users.tests.factory import ProfileFactory, UserFactory


def make_profile(username):
    return ProfileFactory(user=UserFactory(username=username))


class SearchContentTestCase(TestCase):
    """Two markers and two objects whose names, authors and uploaders differ."""

    def setUp(self):
        self.user = UserFactory(username="searcher")
        self.profile = ProfileFactory(user=self.user)
        self.client.force_login(self.user)

        self.first_uploader = make_profile("first_uploader")
        self.second_uploader = make_profile("second_uploader")

        self.abaporu = MarkerFactory(
            title="Abaporu", author="Tarsila do Amaral", owner=self.first_uploader
        )
        self.bananal = MarkerFactory(
            title="Bananal", author="Lasar Segall", owner=self.second_uploader
        )
        self.parangole = ObjectFactory(
            title="Parangole", author="Helio Oiticica", owner=self.first_uploader
        )
        self.bicho = ObjectFactory(
            title="Bicho", author="Lygia Clark", owner=self.second_uploader
        )


class TestSearchInSelectionModals(SearchContentTestCase):
    """The HTMX lists in the artwork and exhibit creation modals."""

    def get_elements(self, **params):
        return self.client.get(
            reverse("get-element"), {"page": "1", **params}, HTTP_HX_REQUEST="true"
        )

    def listed(self, response):
        return list(response.context["repository_list"])

    def test_without_a_search_everything_is_listed(self):
        response = self.get_elements(element_type="marker")

        assert set(self.listed(response)) == {self.abaporu, self.bananal}

    def test_search_matches_the_title(self):
        response = self.get_elements(element_type="marker", search="abaporu")

        assert self.listed(response) == [self.abaporu]
        assert response.context["search"] == "abaporu"

    def test_search_matches_the_credited_author(self):
        response = self.get_elements(element_type="object", search="lygia")

        assert self.listed(response) == [self.bicho]

    def test_search_matches_the_uploader_username(self):
        response = self.get_elements(element_type="marker", search="second_uploader")

        assert self.listed(response) == [self.bananal]

    def test_search_is_case_insensitive_and_matches_substrings(self):
        response = self.get_elements(element_type="marker", search="  SEGAL ")

        assert self.listed(response) == [self.bananal]

    def test_search_works_for_sounds(self):
        sound = SoundFactory(title="Batucada", author="Someone", owner=self.profile)
        SoundFactory(title="Silence", author="Nobody", owner=self.profile)

        response = self.get_elements(element_type="sound", search="batuc")

        assert self.listed(response) == [sound]

    def test_no_matches_says_so(self):
        response = self.get_elements(element_type="marker", search="zzzz")

        assert self.listed(response) == []
        self.assertContains(response, "Nothing matches that search.")

    def test_an_empty_list_without_a_search_shows_no_message(self):
        response = self.get_elements(element_type="sound")

        assert self.listed(response) == []
        self.assertNotContains(response, "Nothing matches that search.")

    def test_pagination_counts_only_the_matches(self):
        series = [
            MarkerFactory(title=f"Serie {i}", author="X", owner=self.profile)
            for i in range(5)
        ]

        with patch.object(settings, "MODAL_PAGE_SIZE", 2):
            first = self.get_elements(element_type="marker", search="serie")
            last = self.get_elements(element_type="marker", search="serie", page="3")
            beyond = self.get_elements(element_type="marker", search="serie", page="9")

        assert first.context["num_pages"] == 3
        assert first.context["page_number"] == 1
        self.assertContains(first, 'data-page="1" data-num-pages="3"')
        assert len(self.listed(first)) == 2
        assert last.context["page_number"] == 3
        assert len(self.listed(last)) == 1
        assert self.listed(last)[0] in series
        # A page past the end falls back to the last page of the matches
        assert beyond.context["page_number"] == 3
        assert self.listed(beyond) == self.listed(last)


class TestSearchInSeeAll(SearchContentTestCase):
    """The public "see all" listings of the collection."""

    def see_all(self, which, **params):
        return self.client.get(reverse("see_all"), {"which": which, **params})

    def test_without_a_search_everything_is_listed(self):
        response = self.see_all("marker")

        assert set(response.context["markers"]) == {self.abaporu, self.bananal}
        assert response.context["no_matches"] is False

    def test_search_matches_the_title(self):
        response = self.see_all("object", search="parangole")

        assert list(response.context["objects"]) == [self.parangole]
        self.assertContains(response, 'value="parangole"')

    def test_search_matches_the_credited_author(self):
        response = self.see_all("marker", search="tarsila")

        assert list(response.context["markers"]) == [self.abaporu]

    def test_search_matches_the_uploader_username(self):
        response = self.see_all("object", search="first_uploader")

        assert list(response.context["objects"]) == [self.parangole]

    def test_search_is_case_insensitive(self):
        response = self.see_all("object", search="CLARK")

        assert list(response.context["objects"]) == [self.bicho]

    def test_artworks_match_the_author_username(self):
        artwork = ArtworkFactory(title="Untitled", author=self.second_uploader)
        ArtworkFactory(title="Other", author=self.first_uploader)

        response = self.see_all("artwork", search="second_up")

        assert list(response.context["artworks"]) == [artwork]

    def test_exhibits_match_the_name(self):
        exhibit = ExhibitFactory(name="Mitologia Estendida", slug="mitologia")
        exhibit.exhibit_type = ExhibitTypes.AR
        exhibit.save()

        response = self.see_all("ar-exhibit", search="mitologia")

        assert list(response.context["ar_exhibits"]) == [exhibit]

    def test_no_matches_says_so(self):
        response = self.see_all("marker", search="zzzz")

        assert response.context["no_matches"] is True
        assert list(response.context["markers"]) == []
        self.assertContains(response, "Nothing matches that search.")
        self.assertNotContains(response, "We found no content on your Collection")

    def test_pagination_keeps_the_search(self):
        series = [
            MarkerFactory(title=f"Serie {i}", author="X", owner=self.profile)
            for i in range(5)
        ]

        with patch.object(settings, "PAGE_SIZE", 2):
            response = self.see_all("marker", search="serie", page="3")

        markers = response.context["markers"]
        assert markers.paginator.count == 5
        assert len(markers) == 1
        assert markers[0] in series
        self.assertContains(response, "?which=marker&page=2&search=serie")

    def test_a_page_past_the_end_redirects_without_losing_the_search(self):
        with patch.object(settings, "PAGE_SIZE", 2):
            response = self.see_all("marker", search="abaporu", page="5")

        assert response.status_code == 302
        assert response.url == reverse("see_all", args=["marker"]) + "?search=abaporu"


class TestSearchDoesNotNarrowSubmittedSelections(SearchContentTestCase):
    """Selections are checked against all content, whatever the search was."""

    def test_artwork_accepts_a_marker_and_object_outside_the_search(self):
        ar_object = ObjectFactory(
            title="Peixe",
            author="Someone",
            owner=self.profile,
            source=get_example_object("peixe.gif"),
        )
        url = reverse("create-artwork") + "?search=abaporu"
        data = {
            "title": "My Test Artwork",
            "description": "This is a test artwork.",
            "scale": 1.5,
            "position_x": 1,
            "position_y": 1,
            "selected_marker": self.bananal.id,
            "selected_object": ar_object.id,
            "search": "abaporu",
        }

        response = self.client.post(url, data)

        assert response.status_code == 302
        artwork = Artwork.objects.get()
        assert artwork.marker == self.bananal
        assert artwork.augmented == ar_object

    def test_mr_exhibit_accepts_objects_outside_the_search(self):
        url = reverse("create-mr-exhibit") + "?search=parangole"
        data = {
            "name": "Searched Exhibit",
            "slug": "searched-exhibit",
            "augmenteds": f"{self.bicho.id}",
            "search": "parangole",
        }

        response = self.client.post(url, data)

        assert response.status_code == 302
        exhibit = Exhibit.objects.get(slug="searched-exhibit")
        assert list(exhibit.augmenteds.all()) == [self.bicho]
