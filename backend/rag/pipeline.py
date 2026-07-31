"""End-to-end RAG pipeline orchestration."""

import logging
from typing import Any

from backend.rag.prompt import build_prompt
from backend.rag.retriever import retrieve_context
from backend.services import llm_service

logger = logging.getLogger(__name__)


def answer_question(question: str) -> dict[str, Any]:
    """Retrieve relevant chunks, build prompt, and generate answer."""

    logger.info("Starting RAG pipeline for question: %s", question)

    context_chunks = retrieve_context(question, top_k=5)

    print("\n========== RETRIEVED CONTEXT ==========")
    print(context_chunks)
    print("=======================================\n")

    context_text: list[str] = []

    # Extract content safely
    if isinstance(context_chunks, list):
        for chunk in context_chunks:
            if isinstance(chunk, dict):
                content = chunk.get("content", "")
                if content:
                    context_text.append(str(content))

            elif isinstance(chunk, str):
                context_text.append(chunk)

    logger.info("Retrieved %d context chunks.", len(context_text))

    print("\n========== CONTEXT TEXT ==========")
    print(context_text)
    print("==================================\n")

    prompt = build_prompt(question, context_text)

    print("\n========== FINAL PROMPT ==========")
    print(prompt)
    print("==================================\n")

    answer = llm_service.generate_answer(prompt)

    return {
        "answer": answer,
        "sources": context_text,
        "prompt": prompt,
    }