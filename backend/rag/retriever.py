"""Retrieval logic for finding relevant document chunks."""

import logging
from typing import Any

from backend.services.embedding_service import search_similar_chunks

logger = logging.getLogger(__name__)


def retrieve_context(question: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Retrieve the most relevant document chunks for a user question."""
    logger.info("Retrieving context for question: %s", question)

    results = search_similar_chunks(question, top_k=top_k)

    documents: list[dict[str, Any]] = []
    if isinstance(results, dict):
        raw_documents = results.get("documents", []) or []
        if raw_documents and isinstance(raw_documents[0], list):
            for chunk_list in raw_documents:
                for chunk in chunk_list:
                    if isinstance(chunk, str):
                        documents.append({"content": chunk})
        elif isinstance(raw_documents, list):
            for chunk in raw_documents:
                if isinstance(chunk, str):
                    documents.append({"content": chunk})
                elif isinstance(chunk, dict):
                    documents.append(chunk)

    if not documents:
        logger.warning("No matching document chunks were found for the question.")

    return documents
