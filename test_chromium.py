# test_chromium.py
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://web.whatsapp.com")
    print("✅ WhatsApp page opened. Close window to exit.")
    input("Press Enter to close...")
    browser.close()