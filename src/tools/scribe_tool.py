# src/tools/scribe_tool.py

# 📦 Import libraries
import os
import csv
from datetime import datetime

# 🛠️ Corrected import for logging
from src.tools.logger_tool import log_event

# 📂 Define output CSV path
OUTPUT_FILE = "output/application_results.csv"

def record_application_result(link, status, job_summary):
    """
    Records the application result into a CSV file.
    
    Args:
        link (str): Job link applied to.
        status (str): Application result (Success / Human Intervention / Failed).
        job_summary (dict): Job details extracted.
    """
    os.makedirs("output", exist_ok=True)
    is_new_file = not os.path.exists(OUTPUT_FILE)

    with open(OUTPUT_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # ✏️ Write header if new file
        if is_new_file:
            writer.writerow(["Date", "Time", "Link", "Status", "Job Title", "Company", "Location", "Summary"])

        # 🕰️ Get current date and time
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        # ✏️ Write job application result
        writer.writerow([
            date_str,
            time_str,
            link,
            status,
            job_summary.get("Job Title", ""),
            job_summary.get("Company Name", ""),
            job_summary.get("Location", ""),
            job_summary.get("Summary", "")
        ])

    log_event(f"📝 Job result saved: {status} for {link}")
