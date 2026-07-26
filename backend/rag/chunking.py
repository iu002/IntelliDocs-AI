"""Utilities for splitting extracted document text into smaller chunks."""

from typing import List


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split a long text string into overlapping chunks for retrieval."""
    if not text or not text.strip():
        raise ValueError("Cannot chunk empty text.")

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if overlap < 0:
        raise ValueError("overlap cannot be negative.")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size.")

    words: List[str] = text.split()
    if len(words) <= chunk_size:
        return [text.strip()]

    step: int = chunk_size - overlap
    chunks: List[str] = []
    start_index: int = 0

    while start_index < len(words):
        end_index: int = min(start_index + chunk_size, len(words))
        chunk_words: List[str] = words[start_index:end_index]
        chunk_text_value: str = " ".join(chunk_words).strip()

        if chunk_text_value:
            chunks.append(chunk_text_value)

        if end_index >= len(words):
            break

        start_index += step

    return chunks
