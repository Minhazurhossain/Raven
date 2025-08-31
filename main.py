# main.py
from PyQt6.QtWidgets import QApplication
from gui import WhatsAppGUI
import sys,time

def run_sender_yielding(contact_file, message, media_path=None):
    from session import WhatsAppSession
    from utils import load_contacts
    from sender import MessageSender

    try:
        contacts = load_contacts(contact_file)
        if not contacts:
            yield 0, 1, []
            return

        session = WhatsAppSession()
        if not session.start(headless=False):  # Set True after login
            yield 0, len(contacts), []
            return

        sender = MessageSender(session.page)
        success_count = 0

        for contact in contacts:
            name = contact['name']
            phone = contact['phone']
            msg = message.format(name=name)

            if sender.send_message(phone, msg, media_path):
                success_count += 1
            else:
                pass  # will yield below

            yield success_count, len(contacts), []

        session.close()
        time.sleep(1)
    except Exception as e:
        print(f"Error in run_sender_yielding: {e}")
        yield 0, 1, []
    
# At the bottom of main.py
if __name__ == "__main__":
    print("🟢 App starting...")
    app = QApplication(sys.argv)
    window = WhatsAppGUI()
    window.show()

    # 🔴 TEMP: Call sending directly to test
    # Remove after test
    window.start_sending()

    sys.exit(app.exec())