"""Service for generating answers with Google Gemini."""

import logging
import os
import re
from functools import lru_cache
from typing import Any, Final

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - handled at runtime
    load_dotenv = None

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover - handled at runtime
    genai = None

logger = logging.getLogger(__name__)

if load_dotenv is not None:
    load_dotenv()

MODEL_NAME: Final[str] = "gemini-2.0-flash"
MAX_RETRIES: Final[int] = 3


def _extract_context_answer(prompt: str) -> str:
    """Extract the context snippet from a prompt to build a fallback answer."""
    context_match = re.search(r"Context:\s*(.+)", prompt, re.DOTALL | re.IGNORECASE)
    if context_match:
        context_text = context_match.group(1).strip()
        if context_text:
            cleaned_lines = [line.strip() for line in context_text.splitlines() if line.strip()]
            return " ".join(cleaned_lines)
    return ""


def _build_fallback_answer(prompt: str) -> str:
    """Build a context-based fallback answer when Gemini is unavailable."""
    context_answer = _extract_context_answer(prompt)
    if not context_answer:
        return "I don't have enough document context to answer this question yet."

    return f"Based on the available context, {context_answer}"


@lru_cache(maxsize=1)
def get_model() -> Any:
    """Create and cache the Gemini model instance."""
    if genai is None:
        raise RuntimeError("google-generativeai is required for Gemini integration.")

    api_key: str | None = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set. Please add it to your .env file.")

    genai.configure(api_key=api_key)
    return genai.GenerativeModel(MODEL_NAME)


def generate_answer(prompt: str) -> str:
    """Generate a response from Gemini with basic retry support."""
    logger.info("Generating Gemini response for prompt length: %s", len(prompt))

    try:
        model: Any = get_model()
    except ValueError as exc:
        logger.warning("Gemini initialization failed: %s", exc)
        return _build_fallback_answer(prompt)
    except RuntimeError as exc:
        logger.warning("Gemini service unavailable: %s", exc)
        return _build_fallback_answer(prompt)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = model.generate_content(prompt)
            answer_text = getattr(response, "text", "") or ""
            if answer_text.strip():
                return answer_text.strip()
            break
        except Exception as exc:  # pragma: no cover - defensive handling
            logger.warning("Gemini attempt %s failed: %s", attempt, exc)
            if attempt == MAX_RETRIES:
                return _build_fallback_answer(prompt)

    return _build_fallback_answer(prompt)
