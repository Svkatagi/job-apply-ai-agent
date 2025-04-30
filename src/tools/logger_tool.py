# src/tools/logger_tool.py

# 📦 Import libraries
import os
from datetime import datetime

# 📂 Set log folder and generate new log filename with timestamp
LOG_FOLDER = "output"
os.makedirs(LOG_FOLDER, exist_ok=True)
LOG_FILE = os.path.join(LOG_FOLDER, f"application_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

def log_event(message: str):
    """
    Logs a message with a timestamp into a text file and console.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_message + "\n")
    print(log_message)

def format_exception(e):
    """
    Clean exception message for logging.
    Strips noisy session info and docs.
    """
    raw = getattr(e, 'msg', str(e))
    return raw.split("Session info")[0].split("For documentation")[0].strip()