---
name: gemini-langchain
description: Use when working with the AI integration in interviewi-api/services/gemini_service.py — the LangChain LCEL chain, DB-backed session history keyed by interview_id, JSON output parsing, or stubbed verification of Gemini calls. Trigger keywords: "Gemini", "LangChain", "LCEL", "LLM chain", "chat history", "JsonOutputParser", "RunnableWithMessageHistory", "generate questions", "evaluate answer".
---

# GeminiService (LangChain) patterns

The AI layer is `GeminiService` in `interviewi-api/services/gemini_service.py`. It is a **lazy singleton**: import `get_gemini_service()` and call it — nothing is created at import time, so the app boots without `GOOGLE_API_KEY`. Model comes from `GEMINI_MODEL` env var (default `gemini-2.5-flash`); the DB URL is resolved by `config.resolve_database_url()` (never read raw `DATABASE_URL` here).

## Canonical chain + history pattern (copy this, don't reinvent)

The working design (verified against langchain-core 1.4.x):

```python
# Build: prompt -> raw LLM. NEVER append JsonOutputParser to the chain.
def _build_chain(self, system_prompt: str):
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ])
    return prompt | self.llm

# Invoke: load history -> call -> persist the turn -> return AIMessage
def _invoke_with_history(self, system_prompt, user_input, interview_id):
    history = self._get_session_history(interview_id)
    response = self._build_chain(system_prompt).invoke({
        "input": user_input,
        "history": history.messages,
    })
    history.add_user_message(user_input)
    history.add_ai_message(response.content)
    return response

# Caller: parse the raw text AFTER the call, in a try/except
response = self._invoke_with_history(system_prompt, user_input, interview_id)
result = self.json_parser.parse(response.content)   # JsonOutputParser.parse(text)
```

## Hard rules

1. **Do not wrap the chain in `RunnableWithMessageHistory`.** It is deprecated, and it cannot extract messages from a `JsonOutputParser` (dict/list) output — history silently never persists. Manage history explicitly via `_invoke_with_history`.
2. **Do not put `JsonOutputParser` at the end of the `prompt | llm` chain.** Keep the raw `AIMessage`, store its `.content` in history, and parse afterwards with `self.json_parser.parse(content)`.
3. **Engine `connect_args`**: pass `{"check_same_thread": False}` **only** when `DATABASE_URL` starts with `sqlite`. psycopg2 rejects it (`invalid dsn`) — Postgres is the `config.py` default.
4. **Swallow-and-fall-back**: `generate_questions` returns `[]` on any exception; `evaluate_answer` returns the `_default` dict. Keep that contract — the controller turns an empty result into a `502` + interview deletion.

## Session history

- Keyed by `interview_id` (the `session_id` column of the `langchain_chat_history` table), implemented by `SQLAlchemyChatHistory` (a JSON-blob read-modify-write; `messages_from_dict`/`messages_to_dict`).
- `history.messages` returns `List[BaseMessage]`; `add_user_message` / `add_ai_message` append a turn.
- Non-atomic writes (read-modify-write on one blob): concurrent evaluate calls on the same interview can drop turns. Fine for the single-user wizard.

## Output guardrails (do not skip these)

The LLM's parsed JSON is untrusted — validate before it reaches the DB/results page:

- `_normalize_score(value)` (`gemini_service.py`): coerce to int, clamp to 0-10. Handles numeric strings (`"9"` → 9), floats (`8.6` → 9), out-of-range (`15` → 10), and garbage (`"abc"`, `True`, `None` → 0).
- `_clean_questions(raw)` (`gemini_service.py`): keep only dicts with non-empty `text`, coerce `topic` to str, and normalize `difficulty` to `Easy|Medium|Hard` (unknown → `Medium`).
- `strengths`/`improvements`/`feedback`: only accept lists/strings of the right type — a string passed to a list comprehension iterates **character-by-character** (`"nope"` → `['n','o','p','e']`).

## Verifying without a real API key / quota

The repo has a real pytest suite — **run it**: `python -m pytest -q` from `interviewi-api/`. The `StubLLM` in `tests/conftest.py` replaces the model and `tests/conftest.py` points `DATABASE_URL` at a temp file before importing the app, so tests need no network/key. Use it as the pattern for any new behavior:

```python
# tests/conftest.py — StubLLM is a CALLABLE (LCEL needs a Runnable/callable/dict):
class StubLLM:
    def __init__(self, payload):
        self._payload = payload
    def __call__(self, _input):
        if isinstance(self._payload, Exception):
            raise self._payload
        return type("AIMessage", (), {"content": json.dumps(self._payload)})()

# in a test: swap the live model for the stub
get_gemini_service().llm = StubLLM({"questions": [{"text": "Q", "topic": "t", "difficulty": "easy"}]})
```

For ad-hoc checks outside pytest, drive `get_gemini_service()` directly with `svc.llm = StubLLM(payload)`. Assert on the persisted history (`svc._get_session_history(1).messages`) to prove turns are written. For full-stack checks, stub `get_gemini_service().generate_questions` and use the Flask test client (see `tests/test_api.py` and `add-api-endpoint`).
