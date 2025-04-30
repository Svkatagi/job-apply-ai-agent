# src/agent/decision_maker.py

# 📦 Import necessary libraries
import json
import google.generativeai as genai  # Gemini SDK # type: ignore
from config.settings import GOOGLE_API_KEY 
from src.tools.logger_tool import log_event
from src.tools.token_counter import count_tokens

# 🧠 Configure Gemini model
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-exp")

def decide_next_actions(dom_html: str, memory_data: dict, job_context: dict = {}) -> dict:
    """
    Analyze the DOM and candidate memory to generate next actions for HandsTool.
    
    Args:
        dom_html (str): Full HTML source of the current page.
        memory_data (dict): Candidate FAQ and resume data.
        job_context (dict): Previously extracted job summary (if any).

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
{json.dumps(memory_data, indent=2)}
-----

# 🧠 Previously Extracted Job Context:
-----
{json.dumps(job_context, indent=2)}
-----

# 🎯 Your Task:
1. Carefully analyze the HTML DOM and detect all job-related details.
2. Generate a step-by-step list of actions (click, type, select, upload).
3. Extract the following fields into "job_summary":

- Job Title
- Company Name
- Location
- Location Type
- Employment Type
- Seniority Level
- Summary
- Responsibilities
- Minimum Qualifications
- Preferred Qualifications
- Tech Stack / Skills
- Salary
- Equity
- Perks / Benefits
- Relevance Score (0 to 100): Based on how well the memory_data fits the role.


- The "Summary" field must be a short paragraph (2–3 full sentences) describing the overall role, not a bullet list.
- Do not use bullet points, markdown, or line breaks in the summary.
- Avoid repeating other field content like responsibilities or perks.

4. For each field:
    - If no reliable value can be extracted ➔ set its value to an empty string ("").
    - If a value is already present in job_context, only update if the new value is significantly better (longer, more accurate, more detailed).
    - The "Summary" field must be a short paragraph (2–3 full sentences) describing the overall role, not a bullet list. Avoid markdown, line breaks, or repeating responsibilities.

5. Ensure the Relevance Score reflects how closely the candidate’s profile matches the job (skills, experience, qualifications).

# ⚠️ Special Detection Rules:
- If the page confirms the application is submitted ➔ set "status": "success"
- If the page says you're rejected, spammed, or flagged as a bot ➔ set "status": "failed"
- If CAPTCHA, email verification, or other human-only barriers are detected ➔ set "status": "human_intervention_required", and include "reason"

# 📦 Output Requirements:
- Return ONLY valid JSON.
- Must contain:
    - "status": "action_required" OR "human_intervention_required" OR "success" OR "failed"
    - "actions": [list of action dicts]
    - "job_summary": object with all 15 fields listed above

- Each action must include:
    - "type": one of ["click", "type", "select", "dynamic_select", "check", "upload"]
    - "selector": XPath or CSS
    - Optional fields: "text", "option_text", "file_path"

# ⚡ Important Rules:
- Prefer XPath selectors.
- Do not hallucinate values.
- Match fields exactly from DOM.
- No explanations. Return only the required JSON.

# 📋 Example JSON Output:

{{
  "status": "action_required",
  "actions": [
    {{"type": "type", "selector": "//input[@name='email']", "text": "shreyas@example.com"}},
    {{"type": "upload", "selector": "//input[@type='file']", "file_path": "memory/Resume Shreyas.Katagi.pdf"}},
    {{"type": "click", "selector": "//button[@id='submit-button']"}}
  ],
  "job_summary": {{
    "Job Title": "AI Engineer",
    "Company Name": "OpenAI",
    "Location": "Remote",
    "Location Type": "Remote",
    "Employment Type": "Full-time",
    "Seniority Level": "Mid-Level",
    "Summary": "You'll build LLM-based systems at OpenAI...",
    "Responsibilities": "Develop and deploy GenAI apps...",
    "Minimum Qualifications": "2+ years Python, ML",
    "Preferred Qualifications": "LLM experience, cloud",
    "Tech Stack / Skills": ["Python", "Docker", "LLMs"],
    "Salary": "120000-180000 USD",
    "Equity": "Available",
    "Perks / Benefits": "Health, PTO, remote allowance",
    "Relevance Score": 87
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
        
        # 📋 Show job summary in logs
        # summary = plan.get("job_summary", {})
        # log_event(f"------------------------------- 📋 Gemini job summary: {json.dumps(summary, indent=2)}")
        
        return plan

    except Exception as e:
        log_event(f"⚠️ Failed to generate decision plan: {str(e)}")
        return {}
