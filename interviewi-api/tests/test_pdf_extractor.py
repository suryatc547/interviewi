import io

import pytest
from PyPDF2 import PdfWriter

from services.pdf_extractor import (
    PDFError,
    extract_text_from_pdf,
    sanitize_extracted_text,
    validate_pdf_bytes,
)

# A minimal valid PDF with the text "Hello World" embedded.
# Created manually so tests don't depend on PyPDF2's writer producing
# extractable text (blank pages produce no text).
_SAMPLE_PDF_BYTES = (
    b"%PDF-1.4\n"
    b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
    b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]"
    b"/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj\n"
    b"4 0 obj<</Length 44>>stream\n"
    b"BT /F1 12 Tf 100 700 Td (Hello World) Tj ET\n"
    b"endstream\nendobj\n"
    b"5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\n"
    b"xref\n0 6\n"
    b"0000000000 65535 f \n"
    b"0000000009 00000 n \n"
    b"0000000058 00000 n \n"
    b"0000000115 00000 n \n"
    b"0000000266 00000 n \n"
    b"0000000360 00000 n \n"
    b"trailer<</Size 6/Root 1 0 R>>\n"
    b"startxref\n429\n%%EOF\n"
)

# A blank PDF (no text) — pages exist but extract to empty string
_BLANK_PDF_BYTES = None


def _make_blank_pdf():
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    buf = io.BytesIO()
    writer.write(buf)
    global _BLANK_PDF_BYTES
    _BLANK_PDF_BYTES = buf.getvalue()
    return _BLANK_PDF_BYTES


def _make_pdf_with_text():
    return _SAMPLE_PDF_BYTES


def _make_pdf(text="Sample resume content for testing."):
    """Create an in-memory PDF with extractable text."""
    return io.BytesIO(_SAMPLE_PDF_BYTES)


class _FakeFileStorage:
    """Mimics werkzeug.FileStorage for testing."""

    def __init__(self, data: bytes, filename: str = "test.pdf"):
        self._data = data
        self.filename = filename

    def read(self):
        return self._data


class TestValidatePdfBytes:
    def test_valid_pdf_no_error(self):
        validate_pdf_bytes(_make_pdf_with_text())

    def test_empty_bytes_raises(self):
        with pytest.raises(PDFError, match="empty"):
            validate_pdf_bytes(b"")

    def test_none_raises(self):
        with pytest.raises(PDFError, match="empty"):
            validate_pdf_bytes(None)

    def test_non_pdf_magic_raises(self):
        with pytest.raises(PDFError, match="does not appear to be a valid PDF"):
            validate_pdf_bytes(b"Hello this is a text file")

    def test_too_large_raises(self):
        big = b"%PDF" + b"\x00" * (2 * 1024 * 1024 + 1)
        with pytest.raises(PDFError, match="too large"):
            validate_pdf_bytes(big)


class TestSanitizeExtractedText:
    def test_strips_control_chars(self):
        assert "\x00" not in sanitize_extracted_text("hello\x00world")
        assert "\x07" not in sanitize_extracted_text("hello\x07world")

    def test_collapses_spaces(self):
        result = sanitize_extracted_text("hello    world")
        assert "  " not in result

    def test_collapses_newlines(self):
        result = sanitize_extracted_text("a\n\n\n\n\nb")
        assert "\n\n\n" not in result

    def test_truncates_to_max(self):
        result = sanitize_extracted_text("x" * 20000, max_chars=100)
        assert len(result) == 100 + len("...[truncated]")

    def test_empty_string(self):
        assert sanitize_extracted_text("") == ""

    def test_non_string(self):
        assert sanitize_extracted_text(None) == ""
        assert sanitize_extracted_text(123) == ""


class TestExtractTextFromPdf:
    def test_valid_pdf_with_text(self):
        fake = _FakeFileStorage(_make_pdf_with_text(), "resume.pdf")
        text = extract_text_from_pdf(fake)
        assert len(text) > 0

    def test_blank_pdf_raises(self):
        _make_blank_pdf()
        fake = _FakeFileStorage(_BLANK_PDF_BYTES, "blank.pdf")
        with pytest.raises(PDFError, match="No readable text"):
            extract_text_from_pdf(fake)

    def test_non_pdf_magic_raises(self):
        fake = _FakeFileStorage(b"not a pdf at all", "file.pdf")
        with pytest.raises(PDFError, match="does not appear to be a valid PDF"):
            extract_text_from_pdf(fake)

    def test_empty_file_raises(self):
        fake = _FakeFileStorage(b"", "empty.pdf")
        with pytest.raises(PDFError, match="empty"):
            extract_text_from_pdf(fake)
