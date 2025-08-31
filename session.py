# session.py
from playwright.sync_api import sync_playwright
from config import CHROME_USER_DATA_DIR, WHATSAPP_URL
import os

class WhatsAppSession:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def start(self, headless=True):
        """Launch browser with persistent context"""
        self.playwright = sync_playwright().start()

        # Ensure the user data directory exists
        os.makedirs(CHROME_USER_DATA_DIR, exist_ok=True)

        self.browser = self.playwright.chromium.launch_persistent_context(
            user_data_dir=CHROME_USER_DATA_DIR,
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ],
            viewport={"width": 1366, "height": 768}
        )
        self.page = self.browser.pages[0]
        self.page.goto(WHATSAPP_URL)
        print("Please scan QR code if needed. Waiting for WhatsApp to load...")

        # Wait until logged in
        try:
            self.page.wait_for_selector('div[aria-label="Chat list"]', timeout=60000)
            print("WhatsApp login successful.")
        except:
            raise Exception("Failed to log in to WhatsApp. Please scan QR code.")

    def close(self):
        """Close browser and stop Playwright"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()