# src/tools/scribe_tool.py

# 📦 Import libraries
import os
import csv
from datetime import datetime

# 🛠️ Corrected import for logging
from src.tools.logger_tool import log_event

# 📂 Define output CSV path
#OUTPUT_FILE = "output/application_results.csv"
# 🕰️ Create a unique filename per run (only once)
RUN_TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H%M")
OUTPUT_FILE = f"output/application_results_{RUN_TIMESTAMP}.csv"


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
            writer.writerow([
                "Date", "Time", "Link", "Status",
                "Job Title", "Company Name", "Location", "Location Type", "Employment Type",
                "Seniority Level", "Summary", "Responsibilities",
                "Minimum Qualifications", "Preferred Qualifications",
                "Tech Stack / Skills", "Salary", "Equity", "Perks / Benefits", "Relevance Score"
            ])

        # 🕰️ Get current date and time
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        # 🧠 Extract values safely, join list if needed
        tech_stack = job_summary.get("Tech Stack / Skills", "")
        if isinstance(tech_stack, list):
            tech_stack = "; ".join(tech_stack)

        # ✏️ Write full job result row
        writer.writerow([
            date_str,
            time_str,
            link,
            status,
            job_summary.get("Job Title", ""),
            job_summary.get("Company Name", ""),
            job_summary.get("Location", ""),
            job_summary.get("Location Type", ""),
            job_summary.get("Employment Type", ""),
            job_summary.get("Seniority Level", ""),
            job_summary.get("Summary", ""),
            job_summary.get("Responsibilities", ""),
            job_summary.get("Minimum Qualifications", ""),
            job_summary.get("Preferred Qualifications", ""),
            tech_stack,
            job_summary.get("Salary", ""),
            job_summary.get("Equity", ""),
            job_summary.get("Perks / Benefits", ""),
            job_summary.get("Relevance Score", "")
        ])

    log_event(f"📝 Job result saved: {status} for {link}")
