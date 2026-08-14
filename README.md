# AI Interview Wizard (interviewi)

An intelligent, multi-page technical interview simulator powered by Google Gemini AI. 

This application allows users to generate customized interview questions based on their target role, industry, and skills/experience (optionally grounded in a job description). It guides them through a seamless question-by-question wizard, asynchronously evaluating their answers in the background, and provides comprehensive feedback and scoring upon completion.

## 🌟 Features
- **AI-Powered Question Generation**: Generates relevant technical questions using Google Gemini (default `gemini-2.5-flash`, configurable via `GEMINI_MODEL`).
- **Interactive Multi-Page Wizard**: Focused, one-question-at-a-time user experience with progress tracking.
- **Background Evaluation**: Non-blocking architecture evaluates answers asynchronously as the user progresses.
- **Rich Results Dashboard**: Animated circular score charts and detailed feedback (strengths and areas for improvement).

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
python -m pytest -q        # 31 tests
python -m ruff check .

# Frontend (from web/)
npm run test:ci             # Karma headless
npm run lint
npm run build               # production build
```

---

## 📖 Documentation
Detailed documentation about the architecture and implementation flows can be found in the root directory:
- `IMPLEMENTATION_SUMMARY.md`: Overview of the wizard flow refactor.
- `WIZARD_FLOW_DOCUMENTATION.md`: Deep dive into the multi-page logic.
- `QUICK_START.md`: Additional commands and routing information.
