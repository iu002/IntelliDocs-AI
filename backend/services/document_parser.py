"""Utilities for extracting text from uploaded documents."""

import logging
from pathlib import Path
from typing import Final

try:
    from docx import Document as DocxDocument
except ImportError:  # pragma: no cover - handled at runtime
    DocxDocument = None

try:
    import fitz
except ImportError:  # pragma: no cover - handled at runtime
    fitz = None

logger = logging.getLogger(__name__)
SUPPORTED_EXTENSIONS: Final[set[str]] = {".pdf", ".docx", ".txt"}


def parse_pdf(file_path: str) -> str:
    """Extract text from a PDF file using PyMuPDF."""
    if fitz is None:
        raise RuntimeError("pymupdf is required to parse PDF files.")

    try:
        document = fitz.open(file_path)
    except Exception as exc:  # pragma: no cover - defensive handling
        raise ValueError(f"Unable to open PDF file: {file_path}") from exc

    if document.is_encrypted:
        raise ValueError("The PDF file is encrypted and cannot be read.")

    text_parts: list[str] = []
    for page in document:
        page_text: str = page.get_text()
        if page_text.strip():
            text_parts.append(page_text.strip())

    document.close()

    if not text_parts:
        raise ValueError("The PDF document is empty.")

    logger.info("Extracted PDF text from %s", file_path)
    return "\n\n".join(text_parts)


def parse_docx(file_path: str) -> str:
    """Extract text from a DOCX file using python-docx."""
    if DocxDocument is None:
        raise RuntimeError("python-docx is required to parse DOCX files.")

    try:
        document = DocxDocument(file_path)
    except Exception as exc:  # pragma: no cover - defensive handling
        raise ValueError(f"Unable to read DOCX file: {file_path}") from exc

    paragraphs: list[str] = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
    if not paragraphs:
        raise ValueError("The DOCX document is empty.")

    logger.info("Extracted DOCX text from %s", file_path)
    return "\n\n".join(paragraphs)


def parse_txt(file_path: str) -> str:
    """Extract text from a TXT file using UTF-8 or Windows-1252 decoding."""
    encodings = ("utf-8", "utf-8-sig", "cp1252", "latin-1")
    last_error: Exception | None = None

    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as text_file:
                content: str = text_file.read()
            if content.strip():
                logger.info("Extracted TXT text from %s using %s", file_path, encoding)
                return content.strip()
            raise ValueError("The TXT document is empty.")
        except UnicodeDecodeError as exc:
            last_error = exc
            continue
        except OSError as exc:  # pragma: no cover - defensive handling
            raise ValueError(f"Unable to read TXT file: {file_path}") from exc

    raise ValueError(f"Unable to decode TXT file as UTF-8/CP1252/LATIN-1: {file_path}") from last_error


def extract_text(file_path: str) -> str:
    """Detect the document type and extract text using the matching parser."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")

    extension: str = path.suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported document format: {extension}")

    if extension == ".pdf":
        return parse_pdf(file_path)
    if extension == ".docx":
        return parse_docx(file_path)
    return parse_txt(file_path)
