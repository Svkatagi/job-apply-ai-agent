# src/agent/decision_maker.py

# 📦 Import necessary libraries
import json
import google.generativeai as genai  # Gemini SDK # type: ignore

# 🛠 Correct imports after restructuring
from config.settings import GOOGLE_API_KEY 
from src.tools.logger_tool import log_event
from src.tools.token_counter import count_tokens

# 🧠 Configure Gemini model
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-exp")

def decide_next_actions(dom_html: str, memory_data: dict) -> dict:
    """
    Analyze the DOM and candidate memory to generate next actions for HandsTool.
    
    Args:
        dom_html (str): Full HTML source of the current page.
        memory_data (dict): Candidate FAQ and resume data.

    Returns:
        dict: Action plan and job summary (if extracted).
    """

    log_event("🔎 Asking Gemini to analyze DOM and generate HandsTool actions...")

    # 📝 Prepare the full prompt for Gemini
    prompt = f"""
You are a strict agentic AI working for an Auto-Apply bot.

# 📄 Current Page DOM:
-----
{dom_html}
-----

# 📂 Candidate Memory (for filling forms):
-----
{memory_data}
-----

# 🎯 Your Task:
1. Analyze the DOM carefully.
2. Plan a step-by-step list of actions needed (click, type, select, dynamic_select, check, upload).
3. If visible, scrape key job data (Job Title, Company Name, Location, Salary, Skills, Summary).

# 📦 Output Requirements:
- Return ONLY valid JSON.
- Must contain:
    - "status": "action_required" OR "human_intervention_required"
    - "actions": [list of action dicts]
    - "job_summary": {object} (optional if no job info found)

- Each action dict must have:
    - "type": one of ["click", "type", "select", "dynamic_select", "check", "upload"]
    - "selector": XPath or CSS
    - "text" (for typing)
    - "option_text" (for selects)
    - "file_path" = "memory/Resume Shreyas.Katagi.pdf" (for uploads)

# ⚡ Important Rules:
- Prefer XPath selectors.
- Match labels and fields exactly from DOM.
- If human verification (CAPTCHA, Email OTP) is detected ➔ mark status as "human_intervention_required" and give reason.

# 📋 Example JSON Output:

{{
  "status": "action_required",
  "actions": [
    {{"type": "type", "selector": "//input[@name='email']", "text": "test@example.com"}},
    {{"type": "dynamic_select", "selector": "//input[@placeholder='Select country']", "option_text": "United States"}},
    {{"type": "click", "selector": "//button[@id='submit-button']"}}
  ],
  "job_summary": {{
    "Company Name": "Moondream",
    "Job Title": "MTS - Full Stack",
    "Location": "Seattle, WA",
    "Salary": "50000-180000 USD",
    "Skills": ["Full Stack", "Cloud"],
    "Summary": "Moondream is hiring a full stack engineer..."
  }}
}}

Strictly output valid JSON. No extra text or explanations.
"""

    try:
        # 🔢 Count and log estimated tokens
        token_estimate = count_tokens(prompt)
        log_event(f"🧮 Approx tokens sent to Gemini: {token_estimate}")

        # 🚀 Generate response from Gemini
        response = model.generate_content(prompt)
        response_text = response.text.strip()

        # 🧹 Clean triple backticks if Gemini returns with them
        if response_text.startswith("```"):
            response_text = response_text.strip("`").replace("json", "", 1).strip()
        response_text = response_text.replace("```", "").strip()

        # 🔍 Parse JSON response into dict
        plan = json.loads(response_text)
        log_event(f"✅ Gemini returned structured decision plan.")

        return plan

    except Exception as e:
        log_event(f"⚠️ Failed to generate decision plan: {str(e)}")
        return {}
