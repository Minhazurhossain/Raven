# test_gui_call.py
from main import run_sender_yielding

# Fake data
contact_file = "contacts.csv"
message = "Hi {name}"
media_path = None

print("🎯 Testing run_sender_yielding directly...")
gen = run_sender_yielding(contact_file, message, media_path)
for sent, total, failed in gen:
    print(f"Progress: {sent}/{total}")
    break  # Just test first step
print("✅ Generator works!")