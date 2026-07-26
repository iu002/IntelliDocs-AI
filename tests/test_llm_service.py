import unittest
from unittest.mock import patch

from backend.services import llm_service


class LLMServiceFallbackTests(unittest.TestCase):
    def test_generate_answer_uses_context_when_gemini_is_unavailable(self) -> None:
        prompt = (
            "You are IntelliDocs AI.\n\n"
            "Question: What is the refund policy?\n\n"
            "Context:\nRefunds are available within 30 days for unused products."
        )

        with patch("backend.services.llm_service.get_model", side_effect=RuntimeError("Gemini unavailable")):
            answer = llm_service.generate_answer(prompt)

        self.assertTrue(answer)
        self.assertNotIn("I could not generate", answer)
        self.assertIn("refund", answer.lower())
