from django.test import TestCase
from django.urls import reverse

from core.models import ExhibitTypes
from core.tests.factory import ExhibitFactory


class TestExhibitSelect(TestCase):
    def test_exhibit_select(self):
        """
        Test the exhibit selection page
        """
        e1 = ExhibitFactory(name="Exhibit 1", slug="exhibit-1")
        e2 = ExhibitFactory(name="Exhibit 2", slug="exhibit-2")
        e1.exhibit_type = ExhibitTypes.AR
        e2.exhibit_type = ExhibitTypes.AR
        e1.save()
        e2.save()
        response = self.client.get(reverse("exhibit_select"))

        assert response.status_code == 200
        assert "form" in response.context
        exhibits = response.context["form"].fields["exhibit"].queryset
        assert exhibits.count() == 2
        assert e1 in exhibits
        assert e2 in exhibits

    def test_exhibit_select_with_mr_exhibits(self):
        """
        Test the exhibit selection page doesn't offer MR exhibits
        """
        e1 = ExhibitFactory(
            name="Exhibit 1", slug="exhibit-1", exhibit_type=ExhibitTypes.MR
        )
        e2 = ExhibitFactory(
            name="Exhibit 2", slug="exhibit-2", exhibit_type=ExhibitTypes.MR
        )
        e3 = ExhibitFactory(
            name="Exhibit 3", slug="exhibit-3", exhibit_type=ExhibitTypes.AR
        )
        e4 = ExhibitFactory(
            name="Exhibit 4", slug="exhibit-4", exhibit_type=ExhibitTypes.AR
        )
        e1.exhibit_type = ExhibitTypes.MR
        e2.exhibit_type = ExhibitTypes.MR
        e1.save()
        e2.save()
        e3.exhibit_type = ExhibitTypes.AR
        e4.exhibit_type = ExhibitTypes.AR
        e3.save()
        e4.save()

        response = self.client.get(reverse("exhibit_select"))

        assert response.status_code == 200
        assert "form" in response.context
        exhibits = response.context["form"].fields["exhibit"].queryset
        assert exhibits.count() == 2
        assert e3 in exhibits
        assert e4 in exhibits
        assert e1 not in exhibits
        assert e2 not in exhibits
