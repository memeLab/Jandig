from django.test import TestCase
from django.urls import reverse

from core.models import ExhibitTypes
from core.tests.factory import ArtworkFactory, ExhibitFactory, ObjectFactory


class TestExhibit(TestCase):
    def test_exhibit(self):
        """
        Test the exhibit selection page
        """
        e1 = ExhibitFactory(name="Exhibit 1", slug="exhibit-1")
        e1.artworks.set({})
        e1.augmenteds.set({})
        e1.exhibit_type = ExhibitTypes.AR
        e1.save()

        assert e1.artworks.count() == 0
        assert e1.augmenteds.count() == 0

        artwork1 = ArtworkFactory(author=e1.owner)
        artwork2 = ArtworkFactory(author=e1.owner)
        e1.artworks.set([artwork1, artwork2])
        e1.save()

        response = self.client.get(reverse("exhibit", kwargs={"slug": e1.slug}))

        assert response.status_code == 200
        artworks = response.context["artworks"]
        assert artworks.count() == e1.artworks.count()

    def test_exhibit_with_artworks_and_objects(self):
        e1 = ExhibitFactory(name="Exhibit 1", slug="exhibit-1")
        e1.artworks.set({})
        e1.augmenteds.set({})
        e1.exhibit_type = ExhibitTypes.AR
        e1.save()
        assert e1.artworks.count() == 0
        assert e1.augmenteds.count() == 0

        artwork1 = ArtworkFactory(author=e1.owner)
        artwork2 = ArtworkFactory(author=e1.owner)
        object1 = ObjectFactory(owner=e1.owner)
        object2 = ObjectFactory(owner=e1.owner)

        e1.artworks.set([artwork1, artwork2])
        e1.augmenteds.set([object1, object2])
        e1.save()
        response = self.client.get(reverse("exhibit", kwargs={"slug": e1.slug}))
        assert response.status_code == 200
        artworks = response.context["artworks"]
        assert artworks.count() == 2

    def test_exhibit_with_no_artworks(self):
        e1 = ExhibitFactory(name="Exhibit 1", slug="exhibit-1")
        e1.artworks.set({})
        e1.augmenteds.set({})
        e1.exhibit_type = ExhibitTypes.AR
        e1.save()

        object1 = ObjectFactory(owner=e1.owner)
        object2 = ObjectFactory(owner=e1.owner)
        e1.augmenteds.set([object1, object2])
        e1.save()
        assert e1.artworks.count() == 0
        assert e1.augmenteds.count() == 2

        response = self.client.get(reverse("exhibit", kwargs={"slug": e1.slug}))

        assert response.status_code == 404
        assert "No artworks found for this exhibit." in str(response.content)
