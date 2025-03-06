from playwright.sync_api import Page, expect


def test_home_loads_in_english(page: Page):
    page.goto("http://localhost:8000/")

    expect(page.locator("#main_title")).to_contain_text("Welcome to Jandig")


def test_changing_language_to_portuguese_and_back_to_english(page: Page) -> None:
    page.goto("http://localhost:8000/")
    page.locator(".trigger-lang-modal").click()
    page.get_by_label("pt-br").check()
    page.get_by_role("button", name="Ok").click()
    expect(page).to_have_url("http://localhost:8000/")

    expect(page.locator("#main_title")).to_contain_text("Bem vindo ao Jandig")
    page.locator(".trigger-lang-modal").click()
    page.get_by_label("en-us").check()
    page.get_by_role("button", name="Ok").click()
    expect(page).to_have_url("http://localhost:8000/")
    expect(page.locator("#main_title")).to_contain_text("Welcome to Jandig")
