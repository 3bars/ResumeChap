"""resume-engine: import/parse resume content from uploaded files.

Supported inputs:
  - .pdf  (via pypdf)
  - .docx (via python-docx)
  - .txt / .md (plain text / markdown)

This module is intentionally isolated so we can grow it later (e.g. richer
structured-field extraction, LinkedIn import, etc.) without touching the API.
"""
import io
from typing import Tuple

from pypdf import PdfReader
import docx


def _parse_pdf(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    parts = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            parts.append(text.strip())
    return "\n\n".join(parts)


def _parse_docx(data: bytes) -> str:
    document = docx.Document(io.BytesIO(data))
    parts = [p.text for p in document.paragraphs if p.text and p.text.strip()]
    return "\n".join(parts)


def _parse_text(data: bytes) -> str:
    for encoding in ("utf-8", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".markdown"}


def parse_file(filename: str, data: bytes) -> Tuple[str, str]:
    """Return (content, content_format) parsed from an uploaded file.

    Raises ValueError for unsupported file types.
    """
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return _parse_pdf(data), "markdown"
    if lower.endswith(".docx"):
        return _parse_docx(data), "markdown"
    if lower.endswith((".txt", ".md", ".markdown")):
        return _parse_text(data), "markdown"
    raise ValueError(
        f"Unsupported file type for '{filename}'. "
        f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
    )
