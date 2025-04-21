from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:8000/"
MAIN_TITLE_LOCATOR = "#main_title"


def test_home_loads_in_english(page: Page):
    page.goto(BASE_URL)

    expect(page.locator(MAIN_TITLE_LOCATOR)).to_contain_text("Welcome to Jandig")


def test_changing_language_to_portuguese_and_back_to_english(page: Page) -> None:
    page.goto(BASE_URL)
    page.locator(".trigger-lang-modal").click()
    page.get_by_label("Brazilian Portuguese").check()
    page.get_by_role("button", name="Ok").click()
    expect(page).to_have_url(BASE_URL)

    expect(page.locator(MAIN_TITLE_LOCATOR)).to_contain_text("Bem vindo ao Jandig")
    page.locator(".trigger-lang-modal").click()
    page.get_by_label("Inglês").check()
    page.get_by_role("button", name="Ok").click()
    expect(page).to_have_url(BASE_URL)
    expect(page.locator(MAIN_TITLE_LOCATOR)).to_contain_text("Welcome to Jandig")
