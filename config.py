# config.py
import os
from datetime import datetime

CHROME_USER_DATA_DIR = os.path.expanduser("~/whatsapp_profile")
WHATSAPP_URL = "https://web.whatsapp.com"
MIN_DELAY = 5
MAX_DELAY = 15
MAX_RETRIES = 3

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
FAILED_DIR = os.path.join(BASE_DIR, "failed_contacts")

# Create directories
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(FAILED_DIR, exist_ok=True)

# Log file
LOG_FILE = os.path.join(LOGS_DIR, f"send_log_{datetime.now().strftime('%Y-%m-%d')}.log")