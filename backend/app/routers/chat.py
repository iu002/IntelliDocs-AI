"""Chat router for question answering through the RAG pipeline."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from backend.rag.pipeline import answer_question

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    """Request body for the chat endpoint."""

    question: str = Field(..., min_length=1, description="The user's question")


@router.post("/chat", status_code=status.HTTP_200_OK)
async def chat(request: ChatRequest) -> dict[str, Any]:
    """Answer a question using the RAG pipeline and Gemini."""
    logger.info("Received chat request: %s", request.question)

    try:
        result: dict[str, Any] = answer_question(request.question)
        answer_text: str = str(result.get("answer", ""))
        success_value: bool = not answer_text.startswith("I could not generate")
        return {
            "answer": answer_text,
            "sources": result.get("sources", []),
            "success": success_value,
        }
    except RuntimeError as exc:
        logger.exception("Chat request failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
    except Exception as exc:  # pragma: no cover - defensive handling
        logger.exception("Unexpected error in chat route: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process the chat request.",
        ) from exc
