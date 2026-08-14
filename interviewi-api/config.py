import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent


def resolve_database_url(url=None):
    """
    Resolve DATABASE_URL so Flask-SQLAlchemy and GeminiService share one DB.

    A relative sqlite path (`sqlite:///interview.db`) is ambiguous: Flask
    resolves it under `<app>/instance`, while a raw SQLAlchemy engine resolves
    it against the process CWD — producing two different DB files. Normalize it
    to an absolute path under interviewi-api/instance so both engines agree.
    """
    url = url or os.getenv(
        "DATABASE_URL", "postgresql://postgres:password@localhost/interviewi"
    )
    if url.startswith("sqlite:///") and not url.startswith("sqlite:////"):
        rel = url[len("sqlite:///"):]
        if not os.path.isabs(rel):
            instance_dir = PROJECT_ROOT / "instance"
            instance_dir.mkdir(exist_ok=True)
            absolute = (instance_dir / rel).resolve()
            url = f"sqlite:///{absolute.as_posix()}"
    return url


class Config:
    SQLALCHEMY_DATABASE_URI = resolve_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
