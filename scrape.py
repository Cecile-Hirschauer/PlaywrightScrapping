from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch()
    page = browser.new_page()
    page.goto('https://www.ch-digital-solutions.fr')
    print(page.title())
    browser.close()

with sync_playwright() as playwright:
    run(playwright)