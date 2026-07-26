"""Health check router for the API."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    """Return a simple health status response."""
    return {"status": "healthy"}
