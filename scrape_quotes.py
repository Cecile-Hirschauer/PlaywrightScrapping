"""Script to scrape quotes from quotes.toscrape.com website."""

from playwright.sync_api import sync_playwright

def run(p):
    """Launch browser, navigate to quotes website and print all quotes."""
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('http://quotes.toscrape.com/')
    
    quotes = page.locator('.text').all_text_contents()
    for quote in quotes:
        print(quote)

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
