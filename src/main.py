# src/main.py

import sys, os, time, json
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import EMAIL_FOR_LOGIN, PASSWORD_FOR_LOGIN
from src.browser.driver_setup import get_driver
from src.agent.decision_maker import decide_next_actions
from src.tools.hands_tool import HandsTool
from src.tools.logger_tool import log_event, format_exception
from src.tools.scribe_tool import record_application_result
from fpdf import FPDF

# 🧹 Close all tabs except the base one
def clean_tabs(driver):
    while len(driver.window_handles) > 1:
        driver.switch_to.window(driver.window_handles[-1])
        driver.close()
    driver.switch_to.window(driver.window_handles[0])

# 📥 Load job links
try:
    df = pd.read_csv("input/job_links.csv")
    job_links = df["Link"].dropna().tolist()
    log_event(f"📥 Loaded {len(job_links)} job links.")
except Exception as e:
    log_event(f"❌ Failed to load job_links.csv: {e}")
    job_links = []

# 🧠 Load memory
try:
    with open("memory/faq_memory.json", "r", encoding="utf-8") as f:
        memory_data = json.load(f)
    log_event("🧠 Memory loaded.")
except Exception as e:
    log_event(f"❌ Failed to load memory: {e}")
    memory_data = {}

# 🖥️ Start browser and tools
driver = get_driver()
hands = HandsTool(driver)
log_event(f"🔗 -------------------------------------------------\n")
log_event(f"🔗 -------------------------------------------------")

retry_tracker = {}

# 🔁 Process each job link
for index, link in enumerate(job_links, start=1):
    try:
        log_event(f"🔢 Job {index} started: {link}")
        clean_tabs(driver)
        driver.get(link)
        time.sleep(3)

        prev_signature = "" # Placeholder for previous signature

        summary = {} # Initialize summary dictionary

        while True:
            # 🔍 Scrape DOM
            dom = driver.page_source # Get the current DOM

            # 📌 Generate a unique signature of the page
            current_url = driver.current_url.split("?")[0]  # Ignore query params
            page_title = driver.title.strip() # Get the page title
            signature = f"{current_url}::{page_title}"  # Create a unique signature for the page
            log_event(f"🧭 Page signature: {signature}")

            # 🤖 Ask Gemini for a plan
            plan = decide_next_actions(dom, memory_data,summary)
            if not plan:
                log_event("⚠️ No plan received. Marking as failed.")
                record_application_result(link, "Failed", summary)
                break

            actions = plan.get("actions", []) # Get actions from plan
            status = plan.get("status", "") # Get status from plan
            reason = plan.get("reason", "") 

            new_summary = plan.get("job_summary", {}) # Get job summary from plan
            summary.update(new_summary)  # this keeps previous values unless Gemini overwrites them
            
            # 📝 Generate cover letter PDF if present
            cover_letter_text = plan.get("cover_letter_text") # Get cover letter text from plan
            if cover_letter_text: # Check if cover letter text is present
                log_event("📄 Generating cover letter PDF...") 
                try:
                    # Convert smart quotes and other unicode to basic ASCII alternatives
                    sanitized_text = cover_letter_text.encode("ascii", "ignore").decode("ascii")

                    pdf = FPDF()
                    pdf.set_auto_page_break(auto=True, margin=15)
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)

                    for line in sanitized_text.split("\n"):
                        pdf.multi_cell(0, 10, line.strip())

                    cover_letter_path = "memory/Shreyas.Katagi Coverletter.pdf"
                    pdf.output(cover_letter_path)
                    log_event("📝 Cover letter PDF generated and saved.")
                except Exception as e:
                    log_event(f"❌ Failed to generate cover letter PDF: {e}")
            else:
                log_event("⚠️ No cover letter text provided. Skipping PDF generation.")
            

            # ✅ Success case (confirmed application)
            if status == "success":
                log_event("🎯 Gemini detected successful application.")
                record_application_result(link, "Success", summary)
                break

            # ❌ Bot/spam/rejected failure
            if status == "failed":
                log_event("🚫 Application was rejected or flagged as spam.")
                record_application_result(link, "Failed", summary)
                break

            # 🛑 Human intervention
            if status == "human_intervention_required":
                log_event(f"🛑 Human intervention required: {reason}")
                record_application_result(link, "Human Intervention", summary)
                break

            if signature != prev_signature: # Check if the page signature has changed
                retry_tracker[signature] = 1 # Reset retry count for new signature
                prev_signature = signature # Update previous signature
                log_event("🔄 New page signature detected. Retry count reset to 1.")
            else:
                retry_tracker[signature] += 1 # Increment retry count for the same signature
                log_event(f"🔁 Retry {retry_tracker[signature]}/3 for signature.")

            if retry_tracker[signature] >= 3: # Check if retry count exceeds 3
                log_event(f"❌ 3 retries for page: {signature}. Marking as failed.")
                record_application_result(link, "Failed", summary) # Mark as failed after 3 retries
                break


            # 🛠️ Execute actions
            if status == "action_required" and actions:
                hands.perform(actions)

                # 🔄 Switch to new tab if opened
                if len(driver.window_handles) > 1:
                    driver.switch_to.window(driver.window_handles[-1])
                    log_event("🧭 Switched to new tab.")

                log_event("🧰 Actions completed.")
                if summary:
                    log_event(f"📋 Job Summary not empty")
                    #log_event(f"📋 Job Summary: {summary}")

                time.sleep(2)

            else:
                log_event(f"ℹ️ Unknown status '{status}'. Marking as failed.")
                record_application_result(link, "Failed", summary)
                break

        # ✅ Cleanup for next link
        clean_tabs(driver)
        log_event(f"✅ Finished job {index}")

    except Exception as e:
        log_event(f"💥 Error on job {index}: {format_exception(e)}")
        record_application_result(link, "Failed", summary)
        clean_tabs(driver)

    log_event(f"🔄 Job {index} cleaned up.")
    log_event(f"🔗 -------------------------------------------------\n")
    log_event(f"🔗 -------------------------------------------------")
    
# 🏁 All done
driver.quit()
log_event("🏁 All job links processed. Browser closed. 🏁")
