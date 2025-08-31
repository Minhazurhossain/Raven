# test_browser.py
from playwright.sync_api import sync_playwright
import time

def test():
    p = sync_playwright().start()
    browser = p.chromium.launch_persistent_context(
        user_data_dir="./test_profile",
        headless=False
    )
    page = browser.pages[0]
    page.goto("https://google.com")
    print("Browser opened. Close window to exit.")
    time.sleep(10)
    browser.close()
    p.stop()

test()