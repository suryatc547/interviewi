# AGENTS.md

Guidance for AI agents working in this repository. Read this before making changes.

## Project overview

**AI Interview Wizard (interviewi)** — a multi-page interview simulator powered by Google Gemini. A user fills in the target **role**, **industry**, and their **skills/experience** (optionally a job description), the backend generates interview questions, the user answers them one at a time in a wizard, and answers are scored by AI in the background. Not IT-specific — works for any role/industry.

Mono-repo with two applications:

| App | Tech | Port | Location |
| --- | --- | --- | --- |
| `interviewi-api` | Python 3.8+, Flask, SQLAlchemy (SQLite/PostgreSQL), LangChain + `langchain-google-genai` | 5000 | `interviewi-api/` |
| `web` | Angular (NgModule, RxJS, plain CSS) | 4200 | `web/` |

Supporting docs in the repo root: `QUICK_START.md`, `WIZARD_FLOW_DOCUMENTATION.md`, `IMPLEMENTATION_SUMMARY.md`, `FEATURE_DOCUMENTATION.md`, `changes/implementation_plan_*.md`.

## Repository layout

```
interviewi-api/
  app.py                       # Flask app factory (create_app), CORS, blueprint registration, logging setup
  config.py                    # Config class + resolve_database_url(); DATABASE_URL, GOOGLE_API_KEY, GEMINI_MODEL
  requirements.txt             # PINNED runtime deps
  requirements-dev.txt         # pytest + ruff
  pytest.ini                   # testpaths=tests, pythonpath=.
  ruff.toml
  .env                         # LOCAL ONLY, gitignored — GOOGLE_API_KEY, DATABASE_URL, etc.
  models/models.py             # SQLAlchemy models: User, Interview, Question, Answer
  controllers/interview_controller.py # Blueprint interview_bp, url_prefix /api/interview
  services/gemini_service.py   # GeminiService (LangChain LCEL) + DB-backed chat history
  services/jd_retriever.py     # RAG for JD-driven questions: sanitize_jd, chunk_jd, BM25 retrieve_chunks
  tests/
    conftest.py                # test app/client fixtures + StubLLM (set env before importing app)
    test_guardrails.py         # _normalize_score, _clean_questions, _clip unit tests
    test_gemini_service.py     # generate/evaluate/history round-trips with StubLLM
    test_api.py                # controller route tests via Flask test client
web/
  package.json                 # Angular 16; scripts include lint (eslint), format (prettier), test:ci
  angular.json                 # project "interviewi-web", app prefix "app"; prod fileReplacements for environments
  karma.conf.js                # Karma (Angular defaults); use `npm run test:ci` headless
  .eslintrc.json               # eslint + @typescript-eslint + eslint-config-prettier
  .prettierrc.json
  src/
    main.ts                    # platformBrowserDynamic bootstrap
    test.ts                    # Karma test bootstrap (zone.js/testing + initTestEnvironment)
    styles.css                 # global plain CSS (no SCSS/preprocessor)
    environments/              # environment.ts + environment.prod.ts (apiUrl)
    app/
      app.module.ts            # declares 4 components; BrowserModule, HttpClientModule, Forms/ReactiveForms
      app-routing.module.ts    # routes below
      models/
        question.model.ts      # shared Question + QuestionAnswer interfaces
      components/
        interview-form/         # class InterviewFormComponent, selector app-interview-form
        question-answer/       # QuestionAnswerComponent
        results/               # ResultsComponent
      services/
        interview.service.ts   # class InterviewService
```

## Frontend routes

| Path | Component | Notes |
| --- | --- | --- |
| `''` | `InterviewFormComponent` | Generate questions |
| `interview/:interviewId` | `QuestionAnswerComponent` | `?question=N` query param (0-based) |
| `results/:interviewId` | `ResultsComponent` | Score + feedback dashboard |
| `**` | redirect to `''` | |

## Backend API (`/api/interview`)

| Method | Route | Purpose | Notes |
| --- | --- | --- | --- |
| POST | `/generate` | Create user+interview, generate questions | 400 missing/invalid fields (role, industry, experience dict) or >20000-char JD; **502 + interview deleted if generation returns no questions** |
| GET | `/questions/<interview_id>` | Questions with latest answer each | 404 if interview not found |
| POST | `/answer` | Save/update an answer | validates length ≤ 5000, 400/404 cases |
| POST | `/evaluate/<answer_id>` | AI-evaluate an answer in the background | updates `ai_score`, `ai_feedback`; also updates question.score |

## Conventions — backend

- **App factory**: `app.py` builds the app, initializes `logging` + CORS + `db`, registers `interview_bp` under `/api/interview`, and calls `db.create_all()`.
- **Models** (`models/models.py`): `db` is a module-level `SQLAlchemy()` instance. Columns use `db.Column`. Timestamps use `datetime.utcnow` with `onupdate` for updated-at fields. `Interview` stores `role`, `industry`, `experience_levels` (JSON `{skill: years}`), and optional `job_description`.
- **Controllers**: Flask blueprints. `try/except Exception` at the route level; on error `logger.error(...)` the exception and return `jsonify({"error": str(e)}), 500` (or rollback first for write routes). Use `db.session.get(Model, id)` — not legacy `Model.query.get(id)`. Import all models at the top of the controller (there is no circular-import reason to import inline).
- **AI service** (`services/gemini_service.py`): **lazy singleton** — import `get_gemini_service()` and call it; nothing is created at import time, so the app boots without `GOOGLE_API_KEY`.
  - Uses LangChain LCEL: `ChatPromptTemplate | ChatGoogleGenerativeAI`. Do **not** put `JsonOutputParser` at the end of the wrapped chain and do **not** use `RunnableWithMessageHistory` (see the `gemini-langchain` skill).
  - Model comes from `GEMINI_MODEL` env var (default `gemini-2.5-flash`).
  - Session history is stored in the `langchain_chat_history` table keyed by `interview_id` and managed through `_invoke_with_history`.
  - DB engine: built from `config.resolve_database_url()`; `connect_args={"check_same_thread": False}` is passed **only for sqlite URLs**; never for Postgres.
  - **JD-grounded questions (RAG)**: `job_description` (optional, stored on `Interview`) is sanitized/chunked/retrieved by `services/jd_retriever.py` (`sanitize_jd`, `chunk_jd`, BM25 `retrieve_chunks`) and injected as a `<job_description>` data-only block by `GeminiService._build_jd_context()` into both `generate_questions` and `evaluate_answer`. No embedding provider/vector DB — keyword retrieval, deterministic and testable. JD is untrusted data: always wrap in data-only tags, never treat as instructions.
- **Environment**: `interviewi-api/.env` is gitignored. `config.py` defaults `DATABASE_URL` to Postgres (`postgresql://postgres:password@localhost/interviewi`) but the checked-in `.env` uses `sqlite:///interview.db`. `.env.example` lists the keys including `GEMINI_MODEL`. A relative sqlite URL is normalized to an absolute path under `interviewi-api/instance/` by `resolve_database_url()` so Flask-SQLAlchemy and `GeminiService` share the same file.

## Conventions — frontend

- **NgModule, not standalone.** Add new components to `app.module.ts` declarations and to `AppModule` imports if they need modules. Do not add to `main.ts`.
- **One folder per component** under `src/app/components/` with `name.component.{ts,css,html}` files.
- **Shared types** go in `src/app/models/` (e.g. `Question`); do not redefine interfaces per component.
- **Service**: `InterviewService` (in `interview.service.ts`, `providedIn: 'root'`) wraps all `HttpClient` calls to `environment.apiUrl` (see `src/environments/`).
- **Subscription style**: components use the `{ next, error }` observer-object form. Errors read `error.error?.error` (backend envelope) with a fallback message. No `pipe`/`takeUntil`/`async pipe` usage anywhere — match that style.
- **Forms**: reactive `FormBuilder` in `InterviewFormComponent` (dynamic `FormArray` of `skill`+`years` rows, required; plus free-text `role`, `industry`, and optional `job_description`); template-driven `[(ngModel)]` in `QuestionAnswerComponent`.
- **CSS**: plain global CSS in `styles.css`; each component has scoped CSS. Bootstrap-style class names (`btn`, `form-control`) are used but Bootstrap is **not installed** — styles are defined in component CSS.

## Commands

```bash
# Backend (from interviewi-api/)
python -m venv venv                      # first time; activate: .\venv\Scripts\Activate (Win)
pip install -r requirements-dev.txt      # runtime + dev deps (pytest, ruff)
python -m pytest -q                      # 56 tests: guardrails, JD/RAG, service round-trips, API routes
python -m ruff check .                   # lint
python app.py                            # http://localhost:5000

# Frontend (from web/)
npm install
npm start                                # ng serve, http://localhost:4200
npm run build                            # production build -> dist/interviewi-web
npm test                                 # Karma/Jasmine (watches by default)
npm run test:ci                          # Karma headless, single run
npm run lint                             # eslint
npm run format                           # prettier --write
```

- **Testing**: backend uses pytest (see `tests/`); the `StubLLM` in `tests/conftest.py` replaces `ChatGoogleGenerativeAI` so tests need no network/API key. Frontend has `interview.service.spec.ts` (HttpClientTestingModule) and a `interview-form.component.spec.ts` smoke test. Match those patterns when adding features.
- **Lint**: backend `ruff` (see `ruff.toml`), frontend `eslint` + `prettier`. Match the surrounding style.

## Known gotchas / landmines

1. **Two engines, one URL**: Flask-SQLAlchemy and `GeminiService` each create their own engine. `config.resolve_database_url()` normalizes a relative sqlite path to `interviewi-api/instance/` so both point at the same file — don't bypass it (e.g. reading raw `DATABASE_URL` in `gemini_service`).
2. **Sqlite single-writer**: two concurrent *write* transactions on one sqlite file raise `database is locked`. `POST /generate` therefore **commits the interview before** calling `generate_questions` (which writes chat history on the service's own connection), and deletes the interview on failure.
3. **Postgres is the config default**: if `DATABASE_URL` is unset or points at Postgres, everything goes through psycopg2 — never pass `check_same_thread` (rejected by psycopg2 as `invalid dsn`).
4. **`generate_questions` returns `[]` on failure** — it swallows exceptions. The controller treats an empty result as a failure (`502` + interview deletion) so no empty interview is persisted.
5. **History writes are non-atomic** (read-modify-write on a JSON blob) — concurrent evaluate calls on the same interview can lose turns. Fine for single-user flows.
6. **Frontend naming is now aligned**: folder `interview-form/` ↔ class `InterviewFormComponent`; file `interview.service.ts` ↔ class `InterviewService`. Keep it that way for new components/services.
7. **API URL is not hardcoded anymore** — it comes from `src/environments/` (per-build `fileReplacements`). The backend must run on port 5000 and CORS must stay enabled (adjust `environment.*.ts` if that ever changes).
8. **`requirements.txt` is pinned** — don't bump LangChain/other deps without re-running the pytest suite (chain/history behavior is version-sensitive).
