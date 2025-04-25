import pytest
import unittest
from playwright.async_api import Page, expect

from core.tests.factory import ExhibitFactory, ArtworkFactory, MarkerFactory, ObjectFactory
BASE_URL = "http://localhost:8000/"

@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.django_db
async def test_collection_works(page: Page):

    ar_object = ObjectFactory.create(title="Test Object")
    marker = MarkerFactory.create(title="Test Marker")
    artwork = ArtworkFactory.create(title="Test Artwork", augmented=ar_object, marker=marker)
    exhibit = ExhibitFactory.create(name="Test Exhibit", artworks=[artwork])
    await page.goto(BASE_URL)
    await page.get_by_role("link", name="Collection").click()


    await expect(page.locator(f"#marker-{marker.id}").get_by_role("img", name=marker.title)).to_be_visible()
    await expect(page.get_by_role("img", name="Test Object")).to_be_visible()
    await expect(page.locator(f"#artwork-{artwork.id} div").first).to_be_visible()

    # page.get_by_role("img", name="Behavior north.").click()
    # page.locator(f"#object-{ar_object.id}").get_by_role("img", name="Bank.").click()
    await page.get_by_role("link", name=exhibit.name).click()




