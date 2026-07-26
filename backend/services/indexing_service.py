"""Service for indexing uploaded documents into the vector database."""

import logging
from pathlib import Path
from typing import Any

from backend.rag.chunking import chunk_text
from backend.services.document_parser import extract_text
from backend.services.embedding_service import create_embeddings, store_embeddings

logger = logging.getLogger(__name__)


def index_document(file_path: str) -> dict[str, Any]:
    """Extract text from a document, chunk it, generate embeddings, and store them."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")

    logger.info("Indexing document: %s", path.name)

    extracted_text: str = extract_text(str(path))
    chunks: list[str] = chunk_text(extracted_text)

    if not chunks:
        raise ValueError("No content was found to index.")

    embeddings: list[list[float]] = create_embeddings(chunks)

    metadata: list[dict[str, Any]] = []
    for chunk_index, chunk in enumerate(chunks):
        metadata.append(
            {
                "filename": path.name,
                "chunk_id": chunk_index,
                "source": str(path),
                "text": chunk,
            }
        )

    store_embeddings(chunks, embeddings, metadata)

    logger.info("Indexed %s chunks from %s", len(chunks), path.name)
    return {"filename": path.name, "chunks": len(chunks)}
