## [v1.0] - 2025-04-29

Initial functional release of the AI Job Application Agent.

### 🚀 Features
- Modular folder structure (`src/`, `tools/`, `memory/`, `input/`, `output/`)
- DOM parsing with Gemini-based action planning
- Hands tool performs form filling, clicks, uploads
- Auto-resume upload using file memory
- Cookie modal dismiss handling
- Token estimation before LLM call
- Full logging per session (timestamped)
- Results saved to structured CSV with date & time

### 🛠 Improvements
- Import path cleanup after restructuring
- Logging formatted and short
- Gemini prompt block cleaned
- Token safety check added
