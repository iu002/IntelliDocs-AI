"""Upload router for document handling."""

import logging
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from pydantic import BaseModel, Field

from backend.services.file_service import save_uploaded_file

logger = logging.getLogger(__name__)
router = APIRouter()


class UploadResponse(BaseModel):
    """Response schema shown in Swagger for successful uploads."""

    success: bool = Field(default=True, description="Indicates whether the upload succeeded")
    filename: str = Field(..., description="The saved filename")
    original_filename: str = Field(..., description="The original uploaded filename")
    file_type: str = Field(..., description="The normalized file extension")
    file_size: str = Field(..., description="The formatted file size")
    message: str = Field(default="Upload successful", description="Status message")


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    response_model=UploadResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        status.HTTP_413_REQUEST_ENTITY_TOO_LARGE: {"description": "File too large"},
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: {"description": "Unsupported file type"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"},
    },
)
async def upload_file(file: UploadFile = File(...)) -> UploadResponse:
    """Accept and save a supported document file."""
    logger.info("Upload request received for: %s", file.filename)

    try:
        saved_file: dict[str, Any] = await save_uploaded_file(file)
        return UploadResponse(
            success=True,
            filename=saved_file.get("filename", ""),
            original_filename=saved_file.get("original_filename", ""),
            file_type=saved_file.get("file_type", ""),
            file_size=saved_file.get("file_size", ""),
            message=saved_file.get("message", "Upload successful"),
        )
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive handling
        logger.exception("Unexpected upload error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process the upload request.",
        ) from exc
