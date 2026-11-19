from django.test import TestCase
from django.urls import reverse

from core.models import ExhibitTypes
from core.tests.factory import ExhibitFactory


class TestExhibitSelectFilter(TestCase):
    @staticmethod
    def make_ar_exhibit(name, slug):
        """ExhibitFactory randomises exhibit_type, so pin it after creation."""
        exhibit = ExhibitFactory(name=name, slug=slug)
        exhibit.exhibit_type = ExhibitTypes.AR
        exhibit.save()
        return exhibit

    def setUp(self):
        self.mitologia = self.make_ar_exhibit(
            "Mitologia Estendida", "mitologia-estendida"
        )
        self.carnaval = self.make_ar_exhibit("Rosas de Ouro", "rosas-de-ouro")

    def options(self, response):
        return list(response.context["form"].fields["exhibit"].queryset)

    def test_without_a_filter_every_ar_exhibit_is_offered(self):
        response = self.client.get(reverse("exhibit_select"))

        assert self.mitologia in self.options(response)
        assert self.carnaval in self.options(response)

    def test_filtering_narrows_the_list(self):
        response = self.client.get(reverse("exhibit_select"), {"search": "mitologia"})

        assert self.options(response) == [self.mitologia]

    def test_filtering_is_case_insensitive_and_matches_substrings(self):
        response = self.client.get(reverse("exhibit_select"), {"search": "OURO"})

        assert self.options(response) == [self.carnaval]

    def test_a_filter_with_no_results_says_so(self):
        response = self.client.get(reverse("exhibit_select"), {"search": "zzzz"})

        assert response.context["no_matches"] is True
        assert self.options(response) == []

    def test_the_search_term_is_kept_in_the_field(self):
        response = self.client.get(reverse("exhibit_select"), {"search": "mitologia"})

        assert response.context["search"] == "mitologia"

    def test_mr_exhibits_are_never_offered(self):
        mr = ExhibitFactory(name="Mitologia MR", slug="mr")
        mr.exhibit_type = ExhibitTypes.MR
        mr.save()

        response = self.client.get(reverse("exhibit_select"), {"search": "mitologia"})

        assert mr not in self.options(response)

    def test_submitting_an_exhibit_filtered_out_of_the_current_view_still_works(self):
        """The POST must validate against every exhibit, not the filtered set."""
        response = self.client.post(
            reverse("exhibit_select"), {"exhibit": self.carnaval.pk}
        )

        assert response.status_code == 302
        assert response.url == "/rosas-de-ouro"
