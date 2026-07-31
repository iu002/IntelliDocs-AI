"""Embedding and vector storage helpers for document retrieval."""

import logging
from pathlib import Path
from typing import Any, Final

import chromadb
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

VECTOR_DB_DIRECTORY: Final[Path] = (
    Path(__file__).resolve().parent.parent / "vector_db"
)

MODEL_NAME: Final[str] = "all-MiniLM-L6-v2"
COLLECTION_NAME: Final[str] = "documents"

VECTOR_DB_DIRECTORY.mkdir(parents=True, exist_ok=True)

# Load embedding model once
model = SentenceTransformer(MODEL_NAME)


def create_embeddings(texts: list[str]) -> list[list[float]]:
    """Create embeddings for text chunks."""
    return model.encode(texts).tolist()


def store_embeddings(
    texts: list[str],
    embeddings: list[list[float]],
    metadata: list[dict[str, Any]],
):
    """Store embeddings in ChromaDB."""

    client = chromadb.PersistentClient(path=str(VECTOR_DB_DIRECTORY))

    # Remove previous collection so only latest document remains
    try:
        client.delete_collection(COLLECTION_NAME)
        logger.info("Deleted previous collection.")
    except Exception:
        logger.info("No previous collection found.")

    collection = client.get_or_create_collection(COLLECTION_NAME)

    ids = [f"doc-{i}" for i in range(len(texts))]

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadata,
    )

    logger.info("Stored %d chunks in ChromaDB.", collection.count())

    return collection


def search_similar_chunks(query: str, top_k: int = 5):
    """Search similar chunks from ChromaDB."""

    client = chromadb.PersistentClient(path=str(VECTOR_DB_DIRECTORY))

    collection = client.get_collection(COLLECTION_NAME)

    print("\n========== COLLECTION ==========")
    print("Collection Name:", COLLECTION_NAME)
    print("Total Chunks:", collection.count())

    query_embedding = model.encode([query]).tolist()[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    print("\n========== USER QUESTION ==========")
    print(query)

    print("\n========== CHROMA RESULTS ==========")
    print(results)
    print("===================================\n")

    documents = results.get("documents", [[]])

    if documents and len(documents[0]) > 0:
        logger.info("Retrieved %d chunks.", len(documents[0]))

        for i, doc in enumerate(documents[0]):
            distance = results["distances"][0][i]
            print(f"\nChunk {i + 1}")
            print(f"Distance: {distance}")
            print(doc[:300])
            print("----------------------------------------")
    else:
        logger.warning("No matching chunks found.")

    return results