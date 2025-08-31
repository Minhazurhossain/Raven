# utils.py
import re
import random
import pandas as pd
import os
from datetime import datetime
import logging
from config import LOG_FILE, TEMPLATES_DIR, FAILED_DIR

# === Logging Setup ===
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

# === Phone Formatting ===
def format_phone_number(phone: str) -> str:
    phone = re.sub(r"[^0-9]", "", str(phone))
    if len(phone) == 10:
        phone = "91" + phone  # Change "91" to your country code if needed
    elif len(phone) > 10 and not phone.startswith("91"):
        phone = "91" + phone
    return phone

# === Load Contacts from CSV or TXT ===
def load_contacts(file_path: str):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Contact file not found: {file_path}")

    contacts = []
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".csv":
        df = pd.read_csv(file_path)
        required_cols = {'name', 'phone'}
        if not required_cols.issubset(df.columns):
            raise ValueError(f"CSV must have columns: {required_cols}")
        contacts = df.to_dict(orient='records')

    elif ext == ".txt":
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
        for line in lines:
            if "-" in line:
                name, phone = line.split("-", 1)
                name, phone = name.strip(), phone.strip()
            else:
                phone = line.strip()
                name = "Customer"
            contacts.append({"name": name, "phone": phone})
    else:
        raise ValueError("File must be .csv or .txt")

    # Validate and format phone numbers
    valid_contacts = []
    for c in contacts:
        try:
            c['phone'] = format_phone_number(c['phone'])
            if len(c['phone']) >= 10:
                valid_contacts.append(c)
            else:
                print(f"❌ Invalid number skipped: {c['phone']}")
        except Exception as e:
            print(f"❌ Failed to parse contact {c}: {e}")
    return valid_contacts

# === Random Delay (5–15 seconds) ===
def random_delay():
    """Wait random time between messages"""
    delay = random.randint(5, 15)
    print(f"⏳ Waiting {delay} seconds before next message...")
    return delay

# === Load Message Templates ===
def load_templates():
    """Load all .txt files from templates/ folder"""
    templates = {}
    if not os.path.exists(TEMPLATES_DIR):
        os.makedirs(TEMPLATES_DIR)
    for file in os.listdir(TEMPLATES_DIR):
        if file.endswith(".txt"):
            with open(os.path.join(TEMPLATES_DIR, file), 'r', encoding='utf-8') as f:
                templates[file.replace(".txt", "")] = f.read().strip()
    return templates

# === Export Failed Contacts to CSV ===
def export_failed_contacts(failed_list, filename=None):
    """Export failed contacts to CSV"""
    if not os.path.exists(FAILED_DIR):
        os.makedirs(FAILED_DIR)
    if not filename:
        filename = f"failed_{datetime.now().strftime('%Y-%m-%d_%H%M')}.csv"
    path = os.path.join(FAILED_DIR, filename)
    pd.DataFrame(failed_list).to_csv(path, index=False)
    print(f"📝 Failed contacts saved to {path}")
    return path