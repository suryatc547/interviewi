---
name: run-dev-stack
description: Use when the user asks to run, start, restart, or troubleshoot the AI Interview Wizard dev stack — the Flask backend (localhost:5000) and/or the Angular frontend (localhost:4200) — or to set up environment/`.env` config. Trigger keywords: "run the app", "start backend", "start frontend", "start the server", "npm start", "dev server", "setup .env".
---

# Run the Interview Wizard dev stack

The app is a mono-repo: `qc-api/` (Flask backend, port 5000) and `web/` (Angular frontend, port 4200). The frontend **requires** the backend on `localhost:5000` — the API URL comes from `web/src/environments/environment.ts` (`apiUrl`, default `http://localhost:5000/api/interview`), swapped via `fileReplacements` for prod builds.

## Backend (`qc-api/`)

1. **Environment file** — `qc-api/.env` must exist (it is gitignored). If missing, copy `.env.example` and fill in at least `GOOGLE_API_KEY`. The checked-in `.env` uses `DATABASE_URL=sqlite:///interview.db` (resolved under `qc-api/instance/`). Optional `GEMINI_MODEL` overrides the model (default `gemini-2.5-flash`). If `DATABASE_URL` is unset, `config.py` defaults to a Postgres URL that will not work locally without a Postgres server.
2. **Virtualenv** — create/activate once:
   ```bash
   python -m venv venv            # first time only
   .\venv\Scripts\Activate        # Windows PowerShell
   pip install -r requirements-dev.txt   # runtime + dev deps (pytest, ruff)
   ```
3. **Run**:
   ```bash
   python app.py                  # Flask dev server on http://localhost:5000
   ```
   `app.py` builds the app via `create_app()`, configures logging, runs `db.create_all()`, and logs to stdout. `use_reloader=False` — restart manually after Python changes.
4. **Sanity checks** (before/after changes): `python -m pytest -q` and `python -m ruff check .` (both from `qc-api/`).

## Frontend (`web/`)

```bash
npm install                       # npm only (no pnpm — pnpm-lock.yaml was removed)
npm start                         # ng serve on http://localhost:4200
```

- The Angular type-check (strict, `strictTemplates`) runs as part of `ng serve`/`ng build` — fix reported type errors rather than only checking the browser console.
- `npm run build` produces `dist/interviewi-web`.
- Lint/format/test: `npm run lint`, `npm run format`, `npm test` (watch) or `npm run test:ci` (ChromeHeadless, single run).

## Verification checklist

1. Backend: `Invoke-RestMethod http://localhost:5000/api/interview/questions/1 -ErrorAction SilentlyContinue` or just open the port — a live backend responds even for unknown IDs (404 JSON, not a connection error).
2. Frontend: open `http://localhost:4200`, the Interview Form should render (no blank page / CORS errors in console).
3. Full flow needs a real `GOOGLE_API_KEY`: form → generate → answer → results.

## Troubleshooting

| Symptom | Cause / fix |
| --- | --- |
| `ValueError: GOOGLE_API_KEY environment variable not set` | `.env` missing or not loaded — `config.py` uses `python-dotenv`; confirm the key is present and restart. |
| `invalid dsn: invalid connection option "check_same_thread"` | `DATABASE_URL` points at Postgres but `connect_args` was passed with `check_same_thread` — that kwarg is sqlite-only (see `gemini_service.py`). |
| `sqlite3.OperationalError: database is locked` | Two concurrent write transactions on one sqlite file. `POST /generate` commits the interview *before* the AI call to avoid this; if you add a route that writes then calls the AI, follow the same pattern. |
| Frontend gets CORS / connection errors | Backend not running on port 5000, or CORS disabled in `app.py`. |
| Empty interview created (`questions: []`) | Generation failed (missing API key, quota). `generate_questions` returns `[]`; the controller deletes the interview and returns `502` so nothing is persisted. |
| Stale behavior after backend edits | `app.py` runs with `use_reloader=False` — restart the process. |
| Two sqlite files confused | `resolve_database_url()` normalizes relative sqlite to `qc-api/instance/` so Flask-SQLAlchemy and `GeminiService` share one file. If data looks "lost", check you're not bypassing it (raw `DATABASE_URL` reads). |
