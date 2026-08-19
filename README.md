# AI Interview Wizard (interviewi)

An intelligent, multi-page technical interview simulator and ATS resume scanner powered by Google Gemini AI. 

This application provides two main features:
1. **Interview Simulator**: Generate customized interview questions based on your target role, industry, and skills/experience (optionally grounded in a job description). Answer them one at a time in a wizard, with background AI evaluation and comprehensive feedback.
2. **ATS Resume Scanner**: Upload a PDF resume and paste a job description to get an ATS compatibility score, keyword analysis, and actionable improvement suggestions.

## 🌟 Features

### Interview Simulator
- **AI-Powered Question Generation**: Generates relevant technical questions using Google Gemini (default `gemini-2.5-flash`, configurable via `GEMINI_MODEL`).
- **Interactive Multi-Page Wizard**: Focused, one-question-at-a-time user experience with progress tracking.
- **Background Evaluation**: Non-blocking architecture evaluates answers asynchronously as the user progresses.
- **Rich Results Dashboard**: Animated circular score charts and detailed feedback (strengths and areas for improvement).

### ATS Resume Scanner
- **PDF Resume Upload**: Drag-and-drop or click-to-upload with validation (2MB max, 50-page limit).
- **ATS Compatibility Scoring**: Overall score (0-100) with category breakdowns (keywords, skills, experience, format).
- **Keyword Analysis**: Shows matched and missing keywords from the job description.
- **Improvement Suggestions**: AI-powered actionable recommendations to improve resume-JD match.

---

## 🏗️ Architecture

The project is structured as a mono-repo divided into two main applications:

- **interviewi-api (Backend)**: Python Flask API utilizing SQLAlchemy (SQLite/PostgreSQL) and LangChain for AI integration.
- **web (Frontend)**: Angular 16 Single Page Application with custom CSS, glassmorphism UI, and RxJS state management.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+ & npm
- Google Gemini API Key

### 1. Backend Setup (`interviewi-api`)
```bash
cd interviewi-api
python -m venv venv
# Windows: .\venv\Scripts\Activate
# Mac/Linux: source venv/bin/activate

pip install -r requirements-dev.txt   # runtime + dev deps (pytest, ruff)

# Create your environment file
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY (GEMINI_MODEL is optional)

# Start the Flask server (runs on http://localhost:5000)
python app.py
```

### 2. Frontend Setup (`web`)
```bash
cd web
npm install

# Start the Angular development server (runs on http://localhost:4200)
npm start
```

### 3. Tests & lint
```bash
# Backend (from interviewi-api/)
python -m pytest -q        # 104 tests
python -m ruff check .

# Frontend (from web/)
npm run test:ci             # Karma headless
npm run lint
npm run build               # production build
```

---

## 📖 Documentation
Detailed documentation about the architecture and implementation flows can be found in the root directory:
- `IMPLEMENTATION_SUMMARY.md`: Overview of the wizard flow refactor and ATS scanner.
- `WIZARD_FLOW_DOCUMENTATION.md`: Deep dive into the multi-page logic.
- `FEATURE_DOCUMENTATION.md`: Feature specs for answer submission and ATS scanner.
- `QUICK_START.md`: Additional commands and routing information.
