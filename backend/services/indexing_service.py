"""Service for indexing uploaded documents into the vector database."""

import logging
from pathlib import Path
from typing import Any

from backend.rag.chunking import chunk_text
from backend.services.document_parser import extract_text
from backend.services.embedding_service import (
    create_embeddings,
    store_embeddings,
)

logger = logging.getLogger(__name__)


def index_document(file_path: str) -> dict[str, Any]:
    """Extract text from a document, chunk it, generate embeddings, and store them."""

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")

    logger.info("Indexing document: %s", path.name)

    # Extract text
    extracted_text = extract_text(str(path))

    print("\n========== EXTRACTED TEXT ==========")
    print(extracted_text[:1000])
    print("===================================\n")

    # Split into chunks
    chunks = chunk_text(extracted_text)

    print("\n========== CHUNKS ==========")
    print("Total Chunks:", len(chunks))

    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i + 1}")
        print(chunk[:300])

    print("===================================\n")

    if not chunks:
        raise ValueError("No content was found to index.")

    embeddings = create_embeddings(chunks)

    metadata = []

    for chunk_index, chunk in enumerate(chunks):
        metadata.append(
            {
                "filename": path.name,
                "chunk_id": chunk_index,
                "source": str(path),
                "text": chunk,
            }
        )

    store_embeddings(
        texts=chunks,
        embeddings=embeddings,
        metadata=metadata,
    )

    logger.info("Indexed %s chunks from %s", len(chunks), path.name)

    return {
        "filename": path.name,
        "chunks": len(chunks),
    }