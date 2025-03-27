"""Script to scrape and print the title of ch-digital-solutions.fr website."""

from playwright.sync_api import sync_playwright

def run(p):
    """Launch browser, navigate to website and print its title."""
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('https://www.ch-digital-solutions.fr')
    print(page.title())
    browser.close()

with sync_playwright() as playwright:
    run(playwright)