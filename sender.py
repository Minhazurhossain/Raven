# sender.py
from utils import random_delay
import time

class MessageSender:
    def __init__(self, page):
        self.page = page

    def send_message(self, phone: str, message: str, media_path: str = None) -> bool:
        print(f"    🔹 send_message: phone={phone}, media={media_path is not None}")

        try:
            url = f"https://web.whatsapp.com/send?phone={phone}"
            if message.strip():
                url += f"&text={message}"
            print(f"    🌐 Going to: {url}")
            self.page.goto(url)

            # Wait for input box
            self.page.wait_for_selector('div[contenteditable="true"][data-tab="10"]', timeout=30000)
            print("    ✅ Input box found.")

            if media_path:
                print("    📎 Attaching file...")
                self.page.click('div[title="Attach"]')
                with self.page.expect_file_chooser() as fc_info:
                    self.page.click('input[type="file"]')
                file_chooser = fc_info.value
                file_chooser.set_files(media_path)
                print("    ✅ File selected.")

                self.page.wait_for_selector('span[data-icon="send"]', timeout=20000)
                if message.strip():
                    self.page.fill('div[contenteditable="true"][data-tab="10"]', message)
                self.page.click('span[data-icon="send"]')
            else:
                print("    ✉️ Sending text message...")
                self.page.press('div[contenteditable="true"][data-tab="10"]', "Enter")

            time.sleep(random_delay())
            return True

        except Exception as e:
            print(f"    ❌ Send failed: {str(e)}")
            return False
        
    def send_bulk(self, contacts, message_template, media_path=None):
        success_count = 0
        total = len(contacts)

        for contact in contacts:
            name = contact['name']
            phone = contact['phone']
            msg = message_template.format(name=name)

            print(f"📤 Sending to {name} ({phone})...")

            try:
                if self.send_message(phone, msg, media_path):
                    success_count += 1
                else:
                    print(f"❌ Failed to send to {name}")
            except Exception as e:
                print(f"💥 Error sending to {name}: {e}")
                # Continue to next contact
            finally:
                # Always yield progress
                yield success_count, total, []

        print(f"✅ Sent {success_count}/{total} messages.")