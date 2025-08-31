# test_import.py
try:
    from sender import MessageSender
    print("✅ Success: MessageSender imported!")
    print(dir(MessageSender))
except Exception as e:
    print("❌ Error:", e)