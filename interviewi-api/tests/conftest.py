import json
import os
import tempfile

import pytest

# Must be set before importing app/config so Config reads the test DB.
os.environ.setdefault("GOOGLE_API_KEY", "test-key")
_TMP = tempfile.mkdtemp(prefix="qcapi_tests_")
os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(_TMP, "test.db").replace("\\", "/")

from app import create_app  # noqa: E402
from models.models import db  # noqa: E402


class StubLLM:
    """Drop-in for ChatGoogleGenerativeAI; supports LCEL `prompt | llm`."""

    def __init__(self, payload):
        self._payload = payload

    def __call__(self, _input):
        if isinstance(self._payload, Exception):
            raise self._payload
        return type("AIMessage", (), {"content": json.dumps(self._payload)})()


@pytest.fixture()
def app():
    application = create_app()
    with application.app_context():
        db.create_all()
    yield application
    with application.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def stub_llm():
    """Swap GeminiService.llm for a stub that returns the given JSON payload.

    Pass an Exception instance to simulate an LLM failure.
    """
    from services.gemini_service import get_gemini_service

    def _factory(payload):
        get_gemini_service().llm = StubLLM(payload)

    return _factory
