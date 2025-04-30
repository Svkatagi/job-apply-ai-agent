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

# 🔁 Process each job link
for index, link in enumerate(job_links, start=1):
    try:
        log_event(f"🔢 Job {index} started: {link}")
        clean_tabs(driver)
        driver.get(link)
        time.sleep(3)

        retries = 0
        prev_plan_hash = None
        prev_dom_hash = None

        while True:
            # 🔍 Scrape DOM
            dom = driver.page_source
            dom_hash = hash(dom)

            # 🤖 Ask Gemini for a plan
            plan = decide_next_actions(dom, memory_data)
            if not plan:
                log_event("⚠️ No plan received. Marking as failed.")
                record_application_result(link, "Failed", {})
                break

            actions = plan.get("actions", [])
            status = plan.get("status", "")
            summary = plan.get("job_summary", {})
            reason = plan.get("reason", "")

            plan_hash = json.dumps(actions, sort_keys=True)

            log_event(f"🧠 Plan hash: {plan_hash[:50]}...")

            # 🛑 Human intervention
            if status == "human_intervention_required":
                log_event(f"🛑 Human intervention required: {reason}")
                record_application_result(link, "Human Intervention", summary)
                break

            # 🔁 Retry if plan + DOM didn't change
            if plan_hash == prev_plan_hash and dom_hash == prev_dom_hash:
                retries += 1
                log_event(f"🔁 Repeated plan (Retry {retries}/3)")
                if retries >= 3:
                    log_event("❌ 3 retries reached. Marking as failed.")
                    record_application_result(link, "Failed", summary)
                    break
            else:
                retries = 0
                prev_plan_hash = plan_hash
                prev_dom_hash = dom_hash

            # 🛠️ Execute actions
            if status == "action_required" and actions:
                hands.perform(actions)

                # 🔄 Switch to new tab if opened
                if len(driver.window_handles) > 1:
                    driver.switch_to.window(driver.window_handles[-1])
                    log_event("🧭 Switched to new tab.")

                log_event("🧰 Actions completed.")
                if summary:
                    log_event(f"📋 Job Summary: {summary}")

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
        record_application_result(link, "Failed", {})
        clean_tabs(driver)

# 🏁 All done
driver.quit()
log_event("🏁 All job links processed. Browser closed.")
