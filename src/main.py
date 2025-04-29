# src/main.py

# 📦 Imports
import sys
import os
import pandas as pd
import json
import time

# 🛠️ Add project root to path so imports work correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 📥 Load modules
from config.settings import EMAIL_FOR_LOGIN, PASSWORD_FOR_LOGIN
from src.browser.driver_setup import get_driver
from src.agent.decision_maker import decide_next_actions
from src.tools.hands_tool import HandsTool
from src.tools.logger_tool import log_event
from src.tools.scribe_tool import record_application_result

# 📂 Load job links from input CSV
try:
    job_links_df = pd.read_csv("input/job_links.csv")
    job_links = job_links_df["Link"].dropna().tolist()
    log_event(f"📥 Loaded {len(job_links)} job link(s) from CSV.")
except Exception as e:
    log_event(f"❌ Failed to load job_links.csv: {e}")
    job_links = []

# 📂 Load memory (FAQ and resume info)
try:
    with open("memory/faq_memory.json", "r", encoding="utf-8") as f:
        memory_data = json.load(f)
    log_event("🧠 Loaded memory memory/faq_memory.json successfully.")
except Exception as e:
    log_event(f"❌ Failed to load memory: {e}")
    memory_data = {}

# 🖥️ Start the browser session
driver = get_driver()
hands = HandsTool(driver)

# 🔁 Loop through each job link
for link in job_links:
    try:
        log_event(f"🌐 Opening job page: {link}")
        driver.get(link)
        time.sleep(3)

        while True:
            # 🧠 Read the updated DOM
            dom_html = driver.page_source

            # 🎯 Get next action plan from Gemini
            plan = decide_next_actions(dom_html, memory_data)

            if not plan:
                log_event("⚠️ No plan received. Skipping link.")
                break

            status = plan.get("status", "")

            # 🛑 Human intervention needed
            if status == "human_intervention_required":
                reason = plan.get("reason", "Unknown reason")
                log_event(f"🛑 Human intervention needed: {reason}")
                record_application_result(link, "Human Intervention", plan.get("job_summary", {}))
                break

            # ✅ Actions needed (click, type, select)
            if status == "action_required":
                actions = plan.get("actions", [])
                if actions:
                    hands.perform(actions)

                    # 🧭 Switch tab if a new one opened
                    if len(driver.window_handles) > 1:
                        driver.switch_to.window(driver.window_handles[-1])
                        log_event("🧭 Switched to newly opened tab.")

                    log_event("🧰 Actions performed successfully.")
                else:
                    log_event("⚠️ No actions found to perform. Skipping link.")
                    break

                # 📋 Job summary extraction if available
                job_summary = plan.get("job_summary", {})
                if job_summary:
                    log_event(f"📋 Scraped Job Summary: {job_summary}")

                # 🔁 Continue looping if no success/fail detected yet
                time.sleep(2)

            else:
                log_event(f"ℹ️ Unknown status: {status}. Skipping.")
                break

    except Exception as e:
        log_event(f"❌ Exception while processing link: {str(e)}")
        record_application_result(link, "Failed", {})

# 🛑 All links done
driver.quit()
log_event("✅ All job links processed and browser closed.")
