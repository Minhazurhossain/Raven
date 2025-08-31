# test_utils.py
try:
    from utils import random_delay
    print("✅ random_delay imported!")
    print(f"Delay: {random_delay()} seconds")
except Exception as e:
    print("❌ Error:", e)