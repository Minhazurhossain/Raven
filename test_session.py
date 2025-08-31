# test_session.py
from session import WhatsAppSession

session = WhatsAppSession()
if session.start(headless=False):
    input("Press Enter to close...")
    session.close()
else:
    print("Failed to start session.")