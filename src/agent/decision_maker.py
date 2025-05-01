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
    with open("memory/sample_cover_letter.txt", "r", encoding="utf-8") as f:
        cover_letter_reference = f.read()
        log_event("📄 Loaded cover letter reference for tone and structure.")

    log_event("🔎 Asking Gemini to analyze DOM and generate HandsTool actions...")

    # 📝 Prepare the full prompt for Gemini
    prompt = f"""
You are a strict, high-precision agentic AI working for an Auto-Apply bot.

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

# 📄 Cover Letter Reference (follow this tone and structure):
-----
{cover_letter_reference}
-----

# 🎯 Your Task:
1. Analyze the DOM thoroughly to:
    - Extract job-related metadata into a structured "job_summary".
    - Plan step-by-step form interaction actions (click, type, select, check, upload).

2. Your output must contain these 15 fields inside "job_summary":
- Job Title
- Company Name
- Location
- Location Type
- Employment Type
- Seniority Level
- Summary (2–3 sentence paragraph)
- Responsibilities
- Minimum Qualifications
- Preferred Qualifications
- Tech Stack / Skills
- Salary
- Equity
- Perks / Benefits
- Relevance Score (0–100): Based on how closely the candidate memory matches this job.

    ⚠️ If any field is not reliably extractable ➔ use an empty string ("").
    ⚠️ If a value already exists in job_context, only update if the new one is significantly better (longer, clearer, more detailed).
    ⚠️ "Summary" must be a concise paragraph. Do not use markdown, line breaks, bullet points, or repeat other fields.

3. For "Relevance Score":
    - Estimate match between memory_data and job qualifications/responsibilities.
    - Consider role, skills, experience, and location alignment.

4. Before suggesting an action:
    - Skip typing if the input field has a non-empty `value` attribute.
    - Skip checking/selecting if the element is already selected (e.g. `checked="true"`).
    - Avoid clicking a submit button if the DOM shows submission confirmation (e.g. "Thank you", "already applied").

5. Always plan only what is **required** based on the current DOM state.
    - Never suggest duplicate or redundant actions.
    - Avoid resubmitting already completed forms.

6. If the DOM includes a file input for "Cover Letter":
    - Generate a tailored professional cover letter under "cover_letter_text".
    - Use information from:
        - memory_data (resume, skills, education, etc.)
        - job_summary (Job Title, Company Name, Responsibilities, etc.)
    - Follow the reference format above.
    - Save it as: memory/Shreyas.Katagi Coverletter.pdf
    - Add an upload action using that file.

7. If no cover letter is required ➔ do not include "cover_letter_text".

# ⚠️ Special Detection Rules:
- If the page confirms that the application has been submitted ➔ set "status": "success"
- If the page indicates rejection, spam detection, or bot behavior ➔ set "status": "failed"
- If human-only challenges like CAPTCHA or email verification appear ➔ set "status": "human_intervention_required" and explain the reason

# 📦 Output Requirements:
- Return ONLY valid JSON.
- Must contain:
    - "status": one of ["action_required", "human_intervention_required", "success", "failed"]
    - "actions": [list of action dicts]
    - "job_summary": object with all 15 fields listed above
    - Optional: "cover_letter_text": string (only if a cover letter is required)

# ⚙️ Action Format:
Each action must include:
    - "type": one of ["click", "type", "select", "dynamic_select", "check", "upload"]
    - "selector": XPath or CSS
    - Optional fields: "text", "option_text", "file_path"

# ⚡ Important Rules:
- Prefer XPath selectors.
- Match field labels and inputs exactly from the DOM.
- Do not hallucinate job fields.
- Do not return markdown or explanations. Only valid JSON.

# 📋 Example JSON Output:

{{
  "status": "action_required",
  "actions": [
    {{
      "type": "upload",
      "selector": "//input[@name='coverLetter']",
      "file_path": "memory/Shreyas.Katagi Coverletter.pdf"
    }},
    {{ "type": "upload", 
       "selector": "//input[@type='resume']", 
       "file_path": "memory/Resume Shreyas.Katagi.pdf" 
    }},
    {{
      "type": "type",
      "selector": "//input[@name='email']",
      "text": "shreyas@example.com"
    }}
  ],
  "job_summary": {{
    "Job Title": "AI Engineer",
    "Company Name": "OpenAI",
    "Location": "Remote",
    "Location Type": "Remote",
    "Employment Type": "Full-time",
    "Seniority Level": "Mid-Level",
    "Summary": "OpenAI is hiring a full-time AI engineer to build LLM-based tools...",
    "Responsibilities": "Build, deploy and test ML models...",
    "Minimum Qualifications": "2+ years Python/ML",
    "Preferred Qualifications": "LLM or GenAI experience",
    "Tech Stack / Skills": ["Python", "Docker", "LLMs"],
    "Salary": "120000-180000 USD",
    "Equity": "Available",
    "Perks / Benefits": "Health, PTO, remote stipend",
    "Relevance Score": 87
  }},
  "cover_letter_text": "Dear Hiring Team at OpenAI,\n\nI'm excited to apply for the AI Engineer role..."
}}

Strictly return valid JSON. No extra explanations.
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
