---
name: add-api-endpoint
description: Use when adding or changing an API endpoint or feature in the AI Interview Wizard that spans backend and/or frontend — e.g. "add an endpoint", "new API route", "implement a feature", "expose question feedback over HTTP". Covers the Flask controller in qc-api/controllers/qc_controller.py, models, the GeminiService, and the Angular InterviewService.
---

# Add an API endpoint end-to-end

Follow the existing layering: **model → service → controller → frontend service → component**. Wire new components into `app.module.ts` (NgModule, never standalone).

## 1. Model (`qc-api/models/models.py`)

- Add/change a class extending `db.Model`. Columns use `db.Column`, timestamps `db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)` for updated-at.
- Tables are auto-created by `create_all()` at app startup — a new model shows up after a backend restart (no migration tooling; existing SQLite DBs will need the table created manually or a fresh DB).

## 2. Service logic (`qc-api/services/gemini_service.py`)

- AI-dependent logic lives on `GeminiService` as a method. See the `gemini-langchain` skill for the exact chain/history pattern — do **not** wrap `JsonOutputParser` output in `RunnableWithMessageHistory`.
- Pure DB/aggregation logic that needs Flask-SQLAlchemy goes in the controller, not `GeminiService` (its engine is separate).
- `GeminiService` is a **lazy singleton**: import `get_gemini_service()` and call it. Nothing is created at import time, so the app boots without `GOOGLE_API_KEY`.

## 3. Route (`qc-api/controllers/qc_controller.py`)

Pattern for every route:

```python
import logging
from flask import Blueprint, jsonify, request
from models.models import db
from services.gemini_service import get_gemini_service

logger = logging.getLogger(__name__)

@interview_bp.route('/<...>', methods=['POST'])
def my_route():
    try:
        data = request.get_json() or {}
        # validate -> return jsonify({"error": "..."}), 400 / 404
        # do work (call get_gemini_service() or db)
        db.session.commit()
        return jsonify({...}), 200
    except Exception as e:
        db.session.rollback()          # only for write routes
        logger.error("Error ...: %s", e)
        return jsonify({"error": str(e)}), 500
```

- Blueprint is `interview_bp` with `url_prefix='/api/interview'` (registered in `app.py`).
- Use `logger.error(...)` — never `print(...)`. Use `db.session.get(Model, id)` — not `Model.query.get(id)`.
- Import all models at the top of the controller; there is no circular-import reason for inline `from models.models import ...`.
- Return the backend error envelope `{"error": str}` on failure — the frontend reads `error.error?.error`.
- On AI-generation routes: if the AI returns empty, delete the interview row (which was committed *before* generation so the service's sqlite connection isn't locked) and return `502` rather than persisting a partial interview (see `generate_interview`).

## 4. Frontend service (`web/src/app/services/qc.service.ts`)

- Add a method to class `InterviewService` using `HttpClient`. Base URL is `environment.apiUrl` (`src/environments/environment.ts`, default `http://localhost:5000/api/interview`).
- Method returns the `Observable` from `http.get/post/...` directly. Components do the subscribing.

## 5. Component wiring

- Add the component class to `app.module.ts` `declarations` and add it to `AppModule` imports if it needs new Angular modules (`FormsModule`, `ReactiveFormsModule`, `HttpClientModule` already there).
- Subscribe with the `{ next, error }` observer-object form; on error use `error.error?.error || '<fallback>'`. Match the repo's no-`pipe`/no-`takeUntil` style.
- Folder/file naming: kebab-case under `src/app/components/<name>/` with `name.component.{ts,css,html}`. Note the existing mismatch (folder `qc-form` contains `InterviewFormComponent`; file `qc.service.ts` contains `InterviewService`) — preserve it, don't "fix" it.

## 6. Verification

Backend: add/adjust **pytest tests** in `qc-api/tests/` (see `test_api.py` — Flask test client with the `stub_llm` fixture, `test_guardrails.py` for pure functions). Run `python -m pytest -q` from `qc-api/` and `python -m ruff check .`. Frontend: add a service spec (`qc.service.spec.ts`, `HttpClientTestingModule`) and/or a component smoke test; run `npm run test:ci`, `npm run lint`, `npm run build` from `web/`.

For AI-dependent logic, drive `get_gemini_service()` directly with `svc.llm = StubLLM(payload)` (see the `gemini-langchain` skill and `tests/conftest.py`).
