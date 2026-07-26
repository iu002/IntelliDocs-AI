"""Embedding and vector storage helpers for document retrieval."""

import logging
from pathlib import Path
from typing import Any, Final

try:
    import chromadb
except ImportError:  # pragma: no cover - handled at runtime
    chromadb = None

try:
    from sentence_transformers import SentenceTransformer
except ImportError:  # pragma: no cover - handled at runtime
    SentenceTransformer = None

logger = logging.getLogger(__name__)
VECTOR_DB_DIRECTORY: Final[Path] = Path(__file__).resolve().parent.parent / "vector_db"
MODEL_NAME: Final[str] = "all-MiniLM-L6-v2"
COLLECTION_NAME: Final[str] = "documents"

VECTOR_DB_DIRECTORY.mkdir(parents=True, exist_ok=True)


def _normalize_vector(embedding: Any) -> list[float]:
    """Convert sentence-transformer outputs into plain lists of floats."""
    if hasattr(embedding, "tolist"):
        embedding = embedding.tolist()

    if isinstance(embedding, list):
        normalized: list[float] = []
        for item in embedding:
            if hasattr(item, "tolist"):
                item = item.tolist()
            if isinstance(item, list):
                normalized.extend(float(sub_item) for sub_item in item)
            else:
                normalized.append(float(item))
        return normalized

    if isinstance(embedding, tuple):
        return [float(item) for item in embedding]

    return [float(embedding)]


def _normalize_embeddings(encoded: Any) -> list[list[float]]:
    """Normalize a batch of embeddings into a list of list[float]."""
    if hasattr(encoded, "tolist"):
        encoded = encoded.tolist()

    if isinstance(encoded, list):
        return [_normalize_vector(item) for item in encoded]

    return [[float(encoded)]]


def load_model() -> Any | None:
    """Load the sentence-transformers embedding model."""
    if SentenceTransformer is None:
        logger.warning("sentence-transformers is not available; embedding generation will be skipped.")
        return None
    return SentenceTransformer(MODEL_NAME)


def create_embeddings(texts: list[str], model: Any | None = None) -> list[list[float]]:
    """Create embeddings for a list of text chunks."""
    active_model: Any | None = model or load_model()
    if active_model is None:
        logger.warning("Using empty embeddings because the embedding model is unavailable.")
        return [[0.0] for _ in texts]

    try:
        encoded = active_model.encode(texts, convert_to_numpy=False)
        return _normalize_embeddings(encoded)
    except Exception as exc:  # pragma: no cover - defensive handling
        logger.warning("Embedding generation failed: %s", exc)
        return [[0.0] for _ in texts]


def store_embeddings(texts: list[str], embeddings: list[list[float]], metadata: list[dict[str, Any]] | None = None) -> Any:
    """Persist embeddings into a local ChromaDB collection."""
    if chromadb is None:
        logger.warning("chromadb is not available; skipping vector storage.")
        return None

    VECTOR_DB_DIRECTORY.mkdir(parents=True, exist_ok=True)

    try:
        client = chromadb.PersistentClient(path=str(VECTOR_DB_DIRECTORY))
        collection = client.get_or_create_collection(name=COLLECTION_NAME)

        ids: list[str] = [f"doc-{index}" for index in range(len(texts))]
        collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadata or [{} for _ in texts],
            ids=ids,
        )
    except Exception as exc:  # pragma: no cover - defensive handling
        logger.warning("Vector storage failed: %s", exc)
        return None

    logger.info("Stored %s embeddings in ChromaDB", len(texts))
    return collection


def search_similar_chunks(query: str, model: Any | None = None, top_k: int = 5) -> Any:
    """Search the ChromaDB collection for the most similar document chunks."""
    if chromadb is None:
        logger.warning("chromadb is not available; returning no chunks.")
        return {"documents": []}

    active_model: Any | None = model or load_model()
    if active_model is None:
        logger.warning("Embedding model is unavailable; returning no chunks.")
        return {"documents": []}

    try:
        encoded_query = active_model.encode([query], convert_to_numpy=False)
        query_embedding = _normalize_embeddings(encoded_query)[0]

        client = chromadb.PersistentClient(path=str(VECTOR_DB_DIRECTORY))
        collection = client.get_collection(name=COLLECTION_NAME)

        return collection.query(query_embeddings=[query_embedding], n_results=top_k)
    except Exception as exc:  # pragma: no cover - defensive handling
        logger.warning("Similarity search failed: %s", exc)
        return {"documents": []}
