"""
Lightweight RAG for job-description-driven interview questions.

No vector store / embedding provider: retrieval is BM25-style keyword scoring
over sentence-chunks of the JD. Deterministic and dependency-free so it works
offline and in the pytest suite. If this ever needs semantic matching, swap
retrieve_chunks() for an embedding + vector-store retriever behind the same
interface (chunks in, ranked chunks out).

All functions treat the JD as *untrusted data*: it may contain prompt-injection
attempts, so callers must wrap retrieved chunks in data-only tags.
"""

import logging
import re
from math import log

logger = logging.getLogger(__name__)

DEFAULT_MAX_JD_CHARS = 20000
DEFAULT_CHUNK_CHARS = 600
DEFAULT_TOP_K = 3

_STOPWORDS = frozenset({
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in",
    "is", "it", "of", "on", "or", "that", "the", "this", "to", "we", "will",
    "with", "you", "your", "our",
})

_CONTROL_STRIP = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")
_SPACE_COLLAPSE = re.compile(r"[ \t]+")


def sanitize_jd(value, max_chars: int = DEFAULT_MAX_JD_CHARS) -> str:
    """
    Guardrail: coerce the JD into a safe, bounded string.

    - Non-string / None input -> "" (a JD is optional).
    - Strips control characters (keeps newlines/tabs so structure survives).
    - Collapses runs of spaces/tabs, strips leading/trailing whitespace.
    - Truncates to `max_chars` (defense-in-depth against prompt bloat; the
      controller separately rejects longer payloads with a 400).
    """
    if not isinstance(value, str):
        return ""
    cleaned = _CONTROL_STRIP.sub("", value)
    cleaned = _SPACE_COLLAPSE.sub(" ", cleaned)
    return cleaned.strip()[:max_chars]


def chunk_jd(text: str, max_chars: int = DEFAULT_CHUNK_CHARS) -> list:
    """
    Split a JD into retrieval chunks.

    Splits on newlines / sentence boundaries and merges short fragments into
    passages no longer than `max_chars` (hard-wrapping any single over-long
    sentence). Returns [] for empty/short input.
    """
    if not text or not text.strip():
        return []
    parts = re.split(r"[\n\r]+|(?<=[.!?])\s+", text)
    chunks = []
    current = ""
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if len(part) > max_chars:
            part = part[:max_chars]
        if len(current) + len(part) + 1 <= max_chars:
            current = f"{current} {part}".strip()
        else:
            if current:
                chunks.append(current)
            current = part
    if current:
        chunks.append(current)
    return chunks


def _tokenize(text: str) -> list:
    tokens = re.findall(r"[a-z0-9+#.]+", (text or "").lower())
    return [t for t in tokens if t not in _STOPWORDS and len(t) > 1]


def _bm25_score(query_tokens: list, doc_tokens: list, doc_freq: dict,
                num_docs: int, avg_dl: float, k1: float = 1.5,
                b: float = 0.75) -> float:
    """BM25 score of one document (token list) against the query tokens."""
    dl = len(doc_tokens)
    if dl == 0:
        return 0.0
    score = 0.0
    for token in query_tokens:
        tf = doc_tokens.count(token)
        if tf == 0:
            continue
        idf = log((num_docs - doc_freq[token] + 0.5) / (doc_freq[token] + 0.5) + 1)
        score += idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (dl / avg_dl)))
    return score


def retrieve_chunks(query: str, chunks: list, k: int = DEFAULT_TOP_K) -> list:
    """
    Retrieve the top-k chunks most relevant to `query` (BM25 keyword scoring).

    Deterministic: ties keep the original chunk order (stable sort). Empty
    query or empty chunks returns the first `k` chunks as-is.
    """
    if not chunks:
        return []
    query_tokens = _tokenize(query)
    if not query_tokens:
        return chunks[:k]
    num_docs = len(chunks)
    doc_tokens = [_tokenize(chunk) for chunk in chunks]
    doc_freq = {
        token: sum(1 for dt in doc_tokens if token in dt)
        for token in set(query_tokens)
    }
    avg_dl = max(1.0, sum(len(dt) for dt in doc_tokens) / num_docs)
    scored = sorted(
        (
            (chunk, _bm25_score(query_tokens, dt, doc_freq, num_docs, avg_dl))
            for chunk, dt in zip(chunks, doc_tokens)
        ),
        key=lambda pair: pair[1],
        reverse=True,
    )
    return [chunk for chunk, _score in scored[:k]]
