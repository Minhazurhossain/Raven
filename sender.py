# sender.py
from config import MAX_RETRIES
from utils import random_delay, log_message
import time
import os

class MessageSender:
    def __init__(self, page):
        self.page = page

    def send_message(self, phone: str, message: str, media_path: str = None) -> bool:
        url = f"https://web.whatsapp.com/send?phone={phone}&text="
        self.page.goto(url)

        try:
            self.page.wait_for_selector('div[contenteditable="true"][data-tab="10"]', timeout=30000)

            if media_path:
                # Click attach
                self.page.click('div[title="Attach"]')
                with self.page.expect_file_chooser() as fc_info:
                    self.page.click('input[type="file"]')
                file_chooser = fc_info.value
                file_chooser.set_files(media_path)

                # Wait for preview
                self.page.wait_for_selector('span[data-icon="send"]', timeout=20000)

                # Add caption
                if message.strip():
                    self.page.fill('div[contenteditable="true"][data-tab="10"]', message)
                self.page.click('span[data-icon="send"]')
            else:
                self.page.fill('div[contenteditable="true"][data-tab="10"]', message)
                self.page.press('div[contenteditable="true"][data-tab="10"]', "Enter")

            log_message(phone, "Unknown", "success")  # You may enhance this later
            time.sleep(random_delay())
            return True

        except Exception as e:
            log_message(phone, "Unknown", "failed", str(e))
            return False

    def send_bulk(self, contacts, message_template, media_path=None, scheduled_time=None):
        from datetime import datetime
        import time as time_module

        if scheduled_time:
            scheduled = datetime.strptime(scheduled_time, "%Y-%m-%d %H:%M")
            now = datetime.now()
            wait = (scheduled - now).total_seconds()
            if wait > 0:
                print(f"🕒 Waiting {wait:.0f} seconds until {scheduled_time}...")
                time_module.sleep(wait)

        success_count = 0
        failed_list = []

        for contact in contacts:
            name = contact.get("name", "Customer")
            phone = contact["phone"]
            message = message_template.format(name=name)

            if self.send_message(phone, message, media_path):
                success_count += 1
            else:
                failed_list.append(contact)

            yield success_count, len(contacts), failed_list