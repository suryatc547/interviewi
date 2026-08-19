"""
PDF text extraction with guardrails for the ATS scanner.

Validates that uploaded files are genuine PDFs (magic-byte check, not just
extension), enforces size/page limits, extracts text page-by-page, and
sanitizes the output (control-char stripping, whitespace collapsing,
length capping) before it reaches the LLM prompt.
"""

import io
import logging
import re

from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)

# 2 MB hard cap for uploaded PDFs
MAX_PDF_BYTES = 2 * 1024 * 1024

# 50-page cap — absurdly long resumes are likely malformed
MAX_PDF_PAGES = 50

# After extraction, cap the text at this many characters (defense-in-depth)
MAX_EXTRACTED_CHARS = 15000

_PDF_MAGIC = b"%PDF"

_CONTROL_STRIP = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")
_SPACE_COLLAPSE = re.compile(r"[ \t]+")
_MULTI_NEWLINE = re.compile(r"\n{3,}")


class PDFError(Exception):
    """Raised when a PDF fails any validation guardrail."""


def validate_pdf_bytes(data: bytes, filename: str = "") -> None:
    """
    Guardrail: reject data that is clearly not a valid PDF.

    Checks performed:
    - data is non-empty bytes
    - file size <= MAX_PDF_BYTES
    - starts with the %PDF magic signature (not just the extension)
    """
    if not isinstance(data, (bytes, bytearray)) or len(data) == 0:
        raise PDFError("Uploaded file is empty or not a valid file.")

    if len(data) > MAX_PDF_BYTES:
        raise PDFError(
            f"PDF file too large ({len(data):,} bytes). "
            f"Maximum allowed is {MAX_PDF_BYTES:,} bytes (2 MB)."
        )

    if not data[:4].startswith(_PDF_MAGIC):
        raise PDFError(
            "The uploaded file does not appear to be a valid PDF. "
            "Please upload a .pdf file."
        )


def extract_text_from_pdf(file_storage) -> str:
    """
    Extract text from a werkzeug FileStorage (or any object with .read()).

    Guardrails applied:
    1. Read raw bytes; validate PDF magic + size BEFORE parsing.
    2. Page count <= MAX_PDF_PAGES.
    3. Extract text page-by-page, skipping pages that raise errors.
    4. Sanitize: strip control chars, collapse whitespace, cap length.
    5. Reject if extracted text is empty (scanned/image-only PDF).

    Returns the sanitized text string.
    Raises PDFError on any validation failure.
    """
    raw = file_storage.read()
    filename = getattr(file_storage, "filename", "") or ""

    validate_pdf_bytes(raw, filename)

    try:
        reader = PdfReader(io.BytesIO(raw))
    except Exception as exc:
        logger.error("PyPDF2 could not open PDF: %s", exc)
        raise PDFError(
            "The file could not be parsed as a PDF. "
            "It may be corrupted or password-protected."
        ) from exc

    page_count = len(reader.pages)
    if page_count == 0:
        raise PDFError("The PDF has no pages.")

    if page_count > MAX_PDF_PAGES:
        raise PDFError(
            f"PDF has {page_count} pages. Maximum allowed is {MAX_PDF_PAGES}."
        )

    pages_text = []
    for i, page in enumerate(reader.pages):
        try:
            text = page.extract_text() or ""
            pages_text.append(text)
        except Exception as exc:
            logger.warning("Failed to extract text from page %d: %s", i + 1, exc)

    combined = "\n".join(pages_text)
    sanitized = sanitize_extracted_text(combined)

    if not sanitized:
        raise PDFError(
            "No readable text found in the PDF. "
            "The file may be a scanned image or contain only graphics."
        )

    return sanitized


def sanitize_extracted_text(text: str, max_chars: int = MAX_EXTRACTED_CHARS) -> str:
    """
    Guardrail: clean extracted PDF text for safe LLM consumption.

    - Strip control characters (keep newlines/tabs for structure).
    - Collapse runs of spaces/tabs.
    - Collapse 3+ consecutive newlines to 2.
    - Strip leading/trailing whitespace.
    - Truncate to max_chars.
    """
    if not isinstance(text, str):
        return ""
    cleaned = _CONTROL_STRIP.sub("", text)
    cleaned = _SPACE_COLLAPSE.sub(" ", cleaned)
    cleaned = _MULTI_NEWLINE.sub("\n\n", cleaned)
    cleaned = cleaned.strip()
    if len(cleaned) > max_chars:
        cleaned = cleaned[:max_chars] + "...[truncated]"
    return cleaned
