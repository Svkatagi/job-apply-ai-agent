# 🤖 AI Job Application Agent (v1)

An autonomous AI-powered agent that applies to jobs online using Google Gemini, Selenium, and persistent memory.

---

## 🚀 What it Does

- Parses job application pages dynamically using Selenium
- Sends DOM + memory context to Gemini for reasoning
- Receives a structured action plan (click/type/upload)
- Executes steps using a hands tool agent
- Logs every action in real time
- Records job outcome with timestamp and job summary
- Works from a list of links in `input/job_links.csv`

---

## 📁 Project Structure

ai-agent/
├── config/              # Settings loaded via .env
├── input/               # CSV list of job links
├── memory/              # Resume + FAQ memory
├── output/              # Logs + application result CSV
├── src/
│   ├── agent/           # Gemini planner
│   ├── browser/         # Chrome driver setup
│   ├── tools/           # Form filler, logger, memory, CSV
│   └── main.py          # Entry point
├── .env                 # API keys & credentials
├── requirements.txt     # Python dependencies
└── README.md

---

## 🧠 Tech Stack

- **LLM Reasoning**: Google Gemini 2.0 Flash
- **Automation**: Selenium WebDriver
- **Memory**: FAQ JSON + resume.txt
- **Logging**: Custom logger per run
- **CSV I/O**: Input jobs + output result tracking

---

## 🛠️ Setup Instructions

# Clone the repo

git clone <https://github.com/><your-username>/ai-job-agent.git
cd ai-job-agent

# Create virtual environment

python -m venv venv
.\venv\Scripts\activate

# Install dependencies

pip install -r requirements.txt

# Add your secrets to .env

EMAIL_FOR_LOGIN=your_email
PASSWORD_FOR_LOGIN=your_password
GOOGLE_API_KEY=your_google_gemini_key

---

## ▶️ Run the Agent

python src/main.py

---

## 📊 Outputs

- `output/application_log_<timestamp>.txt`: Logs all actions
- `output/application_results.csv`: Final job status + date/time

---

## ✅ Features

- Dynamic field detection & interaction
- Multi-step flows handled
- Cookie modal bypass
- Long-term memory integration
- Modular + extensible codebase

---

## 📦 Version

- `v1`: Fully functional, production-grade prototype

---

## 👨‍💻 Author

Built by [Shreyas Katagi](https://www.linkedin.com/in/shreyaskatagi)

---
