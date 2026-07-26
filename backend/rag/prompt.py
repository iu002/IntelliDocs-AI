"""Prompt-building helpers for the RAG pipeline."""

SYSTEM_PROMPT: str = (
    "You are IntelliDocs AI, an AI assistant that answers questions only using the provided "
    "document context. If the answer is not present in the context, clearly state that the "
    "information is unavailable."
)


def build_prompt(question: str, context: list[str]) -> str:
    """Build a single prompt string using the system instruction and retrieved context."""
    context_text: str = "\n\n".join(context)
    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"Question: {question}\n\n"
        f"Context:\n{context_text}"
    )
