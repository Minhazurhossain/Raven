# main.py
from PyQt6.QtWidgets import QApplication
from gui import WhatsAppGUI
from session import WhatsAppSession
from sender import MessageSender
from utils import load_contacts, log_message
import sys

def run_sender_yielding(contact_file, message, media_path=None, scheduled_time=None):
    session = WhatsAppSession()
    if not session.start(headless=True):
        yield 0, 1, []
        return

    sender = MessageSender(session.page)
    try:
        contacts = load_contacts(contact_file)
        if not contacts:
            yield 0, 1, []
            return

        # Use generator from send_bulk
        gen = sender.send_bulk(contacts, message, media_path, scheduled_time)
        for progress in gen:
            yield progress
    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    app = QApplication(sys.argv) 
    window = WhatsAppGUI()
    window.show()
    sys.exit(app.exec())