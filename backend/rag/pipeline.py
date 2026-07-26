"""End-to-end RAG pipeline orchestration."""

import logging
from typing import Any

from backend.rag.prompt import build_prompt
from backend.rag.retriever import retrieve_context
from backend.services import llm_service

logger = logging.getLogger(__name__)


def answer_question(question: str) -> dict[str, Any]:
    """Retrieve relevant chunks, build a prompt, and return a placeholder LLM response."""
    logger.info("Starting RAG pipeline for question: %s", question)

    context_chunks: list[dict[str, Any]] = retrieve_context(question, top_k=5)
    context_text: list[str] = []

    for chunk in context_chunks:
        if isinstance(chunk, dict):
            content: Any = chunk.get("content")
            if isinstance(content, str):
                context_text.append(content)
            elif isinstance(content, list):
                context_text.extend([str(item) for item in content])

    prompt: str = build_prompt(question, context_text)
    logger.info("Built prompt with %s context chunk(s).", len(context_text))

    # Generate the final answer with the Gemini-backed LLM service.
    answer: str = llm_service.generate_answer(prompt)

    return {
        "answer": answer,
        "sources": context_text,
        "prompt": prompt,
    }
