# session.py
from playwright.sync_api import sync_playwright
import os
import time

class WhatsAppSession:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None

    def start(self, headless=False):
        print("📞 Starting WhatsApp session...")
        user_data_dir = os.path.expanduser("~/whatsapp_profile_debug")
        os.makedirs(user_data_dir, exist_ok=True)

        try:
            self.playwright = sync_playwright().start()
            print("✅ Playwright started.")

            self.browser = self.playwright.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=headless,
                args=["--disable-blink-features=AutomationControlled"],
                viewport={"width": 1366, "height": 768}
            )
            print("✅ Browser launched.")

            self.page = self.browser.pages[0]
            self.page.goto("https://web.whatsapp.com")
            print("🌍 Opening WhatsApp...")

            # Wait loop
            for _ in range(60):
                if self.page.query_selector('div[aria-label="Chat list"]'):
                    print("✅ Logged in!")
                    return True
                time.sleep(2)
            print("❌ Timeout: Not logged in.")
            return False

        except Exception as e:
            print(f"❌ Launch failed: {str(e)}")
            return False

    def close(self):
        print("📞 Closing browser...")
        if self.browser:
            self.browser.close()
        if self.playwright:
            import time
            time.sleep(0.5)
            self.playwright.stop()