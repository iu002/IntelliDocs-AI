"""Utility helpers for working with uploaded files."""

from pathlib import Path
from typing import Final

SUPPORTED_EXTENSIONS: Final[set[str]] = {".pdf", ".docx", ".txt"}


def is_supported_extension(filename: str) -> bool:
    """Return True when the file extension is one of the supported types."""
    return Path(filename).suffix.lower() in SUPPORTED_EXTENSIONS


def format_file_size(size_bytes: int) -> str:
    """Convert raw byte values into a human-friendly size string."""
    if size_bytes < 1024:
        return f"{size_bytes} bytes"

    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"

    return f"{size_bytes / (1024 * 1024):.2f} MB"
