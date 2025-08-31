# test_all.py
print("1. Importing session...")
from session import WhatsAppSession

print("2. Starting session...")
session = WhatsAppSession()
if session.start(headless=False):
    input("Press Enter to close...")
    session.close()
else:
    print("Failed to start.")