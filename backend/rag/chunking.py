"""Utilities for splitting extracted document text into smaller chunks."""

from typing import List


def chunk_text(text: str, chunk_size: int = 80, overlap: int = 20) -> List[str]:
    """Split text into smaller overlapping chunks."""

    if not text or not text.strip():
        raise ValueError("Cannot chunk empty text.")

    words: List[str] = text.split()

    chunks: List[str] = []

    step = chunk_size - overlap

    for start in range(0, len(words), step):
        end = start + chunk_size
        chunk = " ".join(words[start:end]).strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(words):
            break

    return chunks