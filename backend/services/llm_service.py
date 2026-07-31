"""Service for generating answers with Google Gemini."""

import logging
import os
import re
from functools import lru_cache
from typing import Any, Final

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

# `google.generativeai` (the "old"/legacy SDK) reached end-of-life on
# Nov 30, 2025 and is no longer supported. If it's installed at all it may
# still work for a while, but the officially supported package going
# forward is `google-genai` (imported as `from google import genai`).
# Run: pip uninstall google-generativeai && pip install google-genai
try:
    from google import genai
except ImportError:
    genai = None

logger = logging.getLogger(__name__)

if load_dotenv is not None:
    load_dotenv()

MODEL_NAME: Final[str] = "gemini-3.6-flash"
MAX_RETRIES: Final[int] = 3


def _extract_context_answer(prompt: str) -> str:
    context_match = re.search(
        r"={5,}\s*DOCUMENT\s*={5,}\s*(.*?)\s*={5,}",
        prompt,
        re.DOTALL | re.IGNORECASE,
    )

    if context_match:
        return context_match.group(1).strip()

    return ""


def _build_fallback_answer(prompt: str, error: Exception | None = None) -> str:
    context = _extract_context_answer(prompt)

    if not context:
        return "I don't have enough document context to answer this question."

    detail = f" ({error})" if error else ""
    logger.warning("Gemini call failed even though context was present%s", detail)
    return (
        "I found relevant document context, but couldn't reach Gemini to "
        f"generate an answer{detail}. Please check the GEMINI_API_KEY and "
        "google-genai setup."
    )


@lru_cache(maxsize=1)
def get_client() -> Any:
    if genai is None:
        raise RuntimeError(
            "google-genai is not installed. Run: pip install google-genai"
        )

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY not found.")

    return genai.Client(api_key=api_key)


def generate_answer(prompt: str) -> str:
    logger.info("Generating Gemini response...")

    try:
        client = get_client()

    except Exception as exc:
        logger.exception(exc)
        return _build_fallback_answer(prompt, error=exc)

    last_error: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )

            answer = getattr(response, "text", "")

            if answer:
                return answer.strip()

        except Exception as exc:
            last_error = exc
            logger.exception("Gemini request failed (attempt %d/%d)", attempt + 1, MAX_RETRIES)

    return _build_fallback_answer(prompt, error=last_error)