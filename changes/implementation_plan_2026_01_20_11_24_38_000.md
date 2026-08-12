# Question Generation Implementation Plan

## Goal Description
Implement a feature to generate interview questions using LangChain and Gemini based on user input (name, email, tech stack, experience). Store this data in PostgreSQL.

## Proposed Changes

### Backend (Python/Flask)

#### [NEW] [requirements.txt](file:///d:/qc/interviewi/interview-api/requirements.txt)
- Add dependencies: `flask`, `flask-cors`, `langchain`, `langchain-google-genai`, `flask-sqlalchemy`, `psycopg2-binary`, `python-dotenv`.

#### [NEW] [app.py](file:///d:/qc/interviewi/interview-api/app.py)
- Main application entry point.
- Initialize Flask, DB, and CORS.
- Register routes.

#### [NEW] [config.py](file:///d:/qc/interviewi/interview-api/config.py)
- Configuration for DB URI and Gemini API Key.

#### [NEW] [models.py](file:///d:/qc/interviewi/interview-api/models/models.py)
- `User`: `id`, `name`, `email`, `created_at`
- `Interview`: `id`, `user_id`, `tech_stack` (String), `experience_levels` (JSON), `created_at`
- `Question`: `id`, `interview_id`, `text`, `topic`, `difficulty`, `score` (Integer, 0-10)

#### [NEW] [gemini_service.py](file:///d:/qc/interviewi/interview-api/services/gemini_service.py)
- `generate_questions(stack, experience_levels)`:
    - Uses LangChain's `ChatGoogleGenerativeAI` and `PromptTemplate`.
    - Returns a list of questions (structured).

#### [NEW] [interview_controller.py](file:///d:/qc/interviewi/interview-api/controllers/interview_controller.py)
- `POST /api/interview/generate`: 
    - Accepts `name`, `email`, `stack`, `experience`.
    - Creates `User` (if new, checking by email) and `Interview`.
    - Calls `GeminiService`.
    - Saves `Questions` to DB with initial score (0 or null).
    - Returns questions.

### Frontend (Angular)

#### [MODIFY] [app.module.ts](file:///d:/qc/interviewi/web/src/app/app.module.ts)
- Add `HttpClientModule`, `FormsModule`, `ReactiveFormsModule`.

#### [NEW] [interview.service.ts](file:///d:/qc/interviewi/web/src/app/services/interview.service.ts)
- `generateQuestions(data: any): Observable<any>`

#### [NEW] [interview-form.component](file:///d:/qc/interviewi/web/src/app/components/interview-form/interview-form.component.ts)
- Form with:
    - Name (Text)
    - Email (Email)
    - Stack (Dropdown: MEAN, MERN, Java Fullstack)
    - Experience Inputs (Dynamic based on stack).

#### [NEW] [question-list.component](file:///d:/qc/interviewi/web/src/app/components/question-list/question-list.component.ts)
- Display list of generated questions.
- Display score (initially 0/10 or hidden if not graded yet).

## Verification Plan

### Automated Tests
- **Backend Test**:
    - Run `python -m unittest tests/test_gemini_service.py`.
    - Manual curl to test `email` and `score` persistence.
- **Frontend Test**:
    - `ng test` to ensure components create.

### Manual Verification
1.  **Start Backend**: `python app.py`
2.  **Start Frontend**: `ng serve`
3.  **Go to Browser**: `http://localhost:4200`
4.  **Fill Form**: Enter Name, Email, Select Stack.
5.  **Submit**: Verify loading state and questions appear.
6.  **Check DB**: Verify `email` in `users` table and `score` column in `questions` table.
