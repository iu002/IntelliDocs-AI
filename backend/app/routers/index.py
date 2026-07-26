"""Router for indexing uploaded files into the vector database."""

import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from backend.services.indexing_service import index_document

logger = logging.getLogger(__name__)

router = APIRouter()


class IndexRequest(BaseModel):
    """Request body for indexing an uploaded file."""

    filename: str = Field(..., min_length=1, description="The uploaded filename to index")


@router.post("/index", status_code=status.HTTP_200_OK)
async def index_file(request: IndexRequest) -> dict[str, Any]:
    """Locate an uploaded file and index it into the vector database."""
    logger.info("Received indexing request for: %s", request.filename)

    upload_directory = Path(__file__).resolve().parent.parent.parent / "uploads"
    file_path = upload_directory / request.filename

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested file was not found in the uploads directory.",
        )

    try:
        result = index_document(str(file_path))
        return {
            "success": True,
            "filename": result.get("filename", request.filename),
            "chunks_indexed": result.get("chunks", 0),
            "message": "Document indexed successfully.",
        }
    except (FileNotFoundError, ValueError) as exc:
        logger.warning("Indexing failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:  # pragma: no cover - defensive handling
        logger.exception("Unexpected indexing error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to index the document.",
        ) from exc
