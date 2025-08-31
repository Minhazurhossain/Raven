# utils.py
import re
import random
import pandas as pd
import os
from datetime import datetime
import logging

# --- Load config values ---
# Since we removed config.py for simplicity, define paths here
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
FAILED_DIR = os.path.join(BASE_DIR, "failed_contacts")

os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(FAILED_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOGS_DIR, f"send_log_{datetime.now().strftime('%Y-%m-%d')}.log")

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def log_message(phone, name, status, error=None):
    if status == "success":
        logging.info(f"✅ Sent to {name} | {phone}")
    else:
        logging.error(f"❌ Failed {name} | {phone} | {error}")

# --- Phone Number Formatting (Bangladesh: 017... → +88017...) ---
def format_phone_number(phone: str) -> str:
    """Convert numbers like 017... → 88017... (used as +88017... in WhatsApp)"""
    phone = re.sub(r"[^0-9]", "", str(phone))
    
    if phone.startswith("01"):      # 017 → 88017
        phone = "88" + phone
    elif phone.startswith("1"):     # 17 → 88017
        phone = "880" + phone
    elif phone.startswith("8801"):  # already good
        pass
    elif phone.startswith("88"):
        if not phone.startswith("880"):
            phone = "880" + phone[2:]
    else:
        raise ValueError(f"Invalid number format: {phone}")

    if not phone.startswith("880") or len(phone) < 11:
        raise ValueError(f"Invalid number after formatting: {phone}")

    return phone  # Will be used in URL as ?phone=88017... → WhatsApp sees +88017

# --- Load Contacts from CSV or TXT ---
def load_contacts(file_path: str):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Contact file not found: {file_path}")

    contacts = []
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".csv":
        df = pd.read_csv(file_path)
        required_cols = {"name", "phone"}
        if not required_cols.issubset(df.columns):
            raise ValueError(f"CSV must have columns: {required_cols}")
        contacts = df.to_dict(orient="records")

    elif ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        for line in lines:
            if "-" in line:
                parts = line.split("-", 1)
                name, phone = parts[0].strip(), parts[1].strip()
            else:
                name, phone = "Customer", line.strip()
            contacts.append({"name": name, "phone": phone})
    else:
        raise ValueError("File must be .csv or .txt")

    # Format phone numbers
    valid_contacts = []
    for c in contacts:
        try:
            c["phone"] = format_phone_number(c["phone"])
            valid_contacts.append(c)
        except Exception as e:
            print(f"❌ Skipping invalid number {c.get('phone')}: {e}")
    return valid_contacts

# --- Random Delay (5–15 seconds) ---
def random_delay():
    delay = random.randint(5, 15)
    print(f"⏳ Waiting {delay} seconds before next message...")
    return delay

# --- Load Message Templates ---
def load_templates():
    """Load all .txt files from templates/ folder as templates"""
    templates = {}
    if not os.path.exists(TEMPLATES_DIR):
        return templates
    for file in os.listdir(TEMPLATES_DIR):
        if file.endswith(".txt"):
            key = file.replace(".txt", "")
            try:
                with open(os.path.join(TEMPLATES_DIR, file), "r", encoding="utf-8") as f:
                    templates[key] = f.read().strip()
            except Exception as e:
                print(f"⚠️ Failed to load template {file}: {e}")
    return templates

# --- Export Failed Contacts ---
def export_failed_contacts(failed_list, filename=None):
    """Save failed contacts to CSV"""
    if not filename:
        filename = f"failed_{datetime.now().strftime('%Y-%m-%d_%H%M')}.csv"
    path = os.path.join(FAILED_DIR, filename)
    pd.DataFrame(failed_list).to_csv(path, index=False)
    print(f"📝 Failed contacts saved to {path}")
    return path