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
    
    Args:
        message (str): The message to log.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"

    # Write the log to the current session's unique log file
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_message + "\n")

    # Also print log to console for real-time visibility
    print(log_message)
