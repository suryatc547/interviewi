# Quick Start Guide

## 🚀 Running the Application

### Step 1: Start Backend
```bash
cd interviewi-api
python app.py
```
Backend runs on: **http://localhost:5000**

### Step 2: Start Frontend
```bash
cd web
npm start
```
Frontend runs on: **http://localhost:4200**

---

## 🌐 Page Routes

| Route | Component | Purpose |
|-------|-----------|---------|
| `/` | InterviewFormComponent | Generate interview questions |
| `/interview/:id` | QuestionAnswerComponent | Answer questions one by one |
| `/results/:id` | ResultsComponent | View scores and feedback |

---

## 🎯 Key Features

### ✅ What It Does
1. **Generate Questions** - AI creates 10 technical interview questions
2. **Answer One-by-One** - Single question display with progress tracking
3. **Auto-Save & Evaluate** - Background AI evaluation (non-blocking)
4. **View Results** - Overall score + detailed feedback for each question

### 🎨 UI Highlights
- Progress bar showing completion
- Character counter (max 5000)
- Color-coded validation
- Animated circular score display
- Expandable feedback cards
- Responsive mobile design

---

## 📋 User Journey

```
Home → Fill Form → Generate Questions
  ↓
Question 1 → Answer → Save & Next
  ↓
Question 2 → Answer → Save & Next
  ↓
... (repeat for all 10 questions)
  ↓
Results Page → View Score → See Feedback
```

---

## 🎨 Score Grading

| Score | Grade | Color |
|-------|-------|-------|
| 9-10 | Excellent | 🟢 Green |
| 7-8.9 | Good | 🟣 Purple |
| 5-6.9 | Average | 🟡 Yellow |
| 3-4.9 | Below Average | 🟠 Orange |
| 0-2.9 | Poor | 🔴 Red |

---

## 🔧 Tech Stack

**Backend:**
- Flask (Python)
- SQLAlchemy (ORM)
- Google Gemini AI

**Frontend:**
- Angular 16
- TypeScript
- RxJS
- Custom CSS

---

## 📁 Project Structure

```
interviewi-api/
  ├── app.py                    # Flask app entry
  ├── models/models.py          # Database models
  ├── controllers/
  │   └── interview_controller.py # API endpoints
  └── services/
      └── gemini_service.py     # AI integration

web/
  ├── src/app/
  │   ├── app-routing.module.ts      # Routes
  │   ├── components/
  │   │   ├── interview-form/        # Home page
  │   │   ├── question-answer/       # Answer page
  │   │   └── results/               # Results page
  │   ├── services/
  │   │   └── interview.service.ts   # API calls
  │   └── environments/              # environment.ts + environment.prod.ts
```

---

## 🎮 Navigation Controls

### Question Answer Page
- **Previous** - Go back one question
- **Skip** - Skip current question
- **Save & Next** - Save answer and advance

### Results Page
- **Retake Interview** - Start over from Q1
- **Start New Interview** - Create new interview

---

## ⚡ Quick Commands

```bash
# Install backend dependencies (runtime + dev)
cd interviewi-api && pip install -r requirements-dev.txt

# Install frontend dependencies
cd web && npm install

# Run backend
cd interviewi-api && python app.py

# Run frontend
cd web && npm start

# Backend tests + lint
cd interviewi-api && python -m pytest -q && python -m ruff check .

# Frontend tests + lint + build
cd web && npm run test:ci && npm run lint && npm run build
```

---

## 🔑 Environment Setup

Create `interviewi-api/.env` (see `.env.example`):
```env
GOOGLE_API_KEY=your_gemini_api_key
DATABASE_URL=sqlite:///interview.db
GEMINI_MODEL=gemini-2.5-flash
```

---

## 📊 API Quick Reference

```bash
# Generate questions
POST /api/interview/generate
Body: { name, email, role, industry, experience: {skill: years}, job_description }

# Get questions
GET /api/interview/questions/:id

# Submit answer
POST /api/interview/answer
Body: { question_id, answer_text }

# Evaluate answer
POST /api/interview/evaluate/:answerId
```

---

## 🐛 Common Issues

**Issue:** Questions not loading
- Check backend is running on port 5000
- Verify CORS is enabled
- Check browser console for errors

**Issue:** AI evaluation not working
- Verify `GOOGLE_API_KEY` in .env
- Check API quota limits
- Review backend logs

**Issue:** Page not found
- Ensure routing module is imported
- Check Angular router configuration
- Verify component declarations

---

## 📖 Documentation Files

- `IMPLEMENTATION_SUMMARY.md` - Complete overview
- `WIZARD_FLOW_DOCUMENTATION.md` - Detailed flow explanation
- `FEATURE_DOCUMENTATION.md` - Original feature specs

---

## ✨ Tips for Best Experience

1. **Use Chrome/Firefox** for best compatibility
2. **Answer thoughtfully** - AI evaluates detail and accuracy
3. **Use all 5000 characters** if needed for complex answers
4. **Review feedback** on results page to improve
5. **Retake interview** to practice and improve scores

---

**Happy Interviewing! 🎯**
