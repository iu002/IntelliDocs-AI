"""Upload router for document handling."""

import logging
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from pydantic import BaseModel, Field

from backend.services.file_service import UPLOAD_DIRECTORY, save_uploaded_file
from backend.services.indexing_service import index_document

logger = logging.getLogger(__name__)

router = APIRouter()


class UploadResponse(BaseModel):
    success: bool
    filename: str
    original_filename: str
    file_type: str
    file_size: str
    message: str


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_file(file: UploadFile = File(...)):
    try:

        # Save file
        saved = await save_uploaded_file(file)

        # NOTE: previously this was built as the relative string
        # "backend/uploads/{filename}", which only resolves correctly when
        # uvicorn's current working directory happens to be the parent of
        # the `backend` package. Any other launch context (IDE run
        # configs, a different cwd, Docker, Vercel, etc.) made this path
        # not exist, so index_document() raised FileNotFoundError here,
        # producing an intermittent 500 that the frontend showed as
        # "Upload Failed" even though the file itself saved fine. Reuse
        # the same absolute directory file_service already saved into.
        upload_path = str(UPLOAD_DIRECTORY / saved["filename"])

        logger.info(f"Indexing file: {upload_path}")

        # Index document
        result = index_document(upload_path)

        logger.info(result)

        return UploadResponse(
            success=True,
            filename=saved["filename"],
            original_filename=saved["original_filename"],
            file_type=saved["file_type"],
            file_size=saved["file_size"],
            message="Upload & Indexed Successfully",
        )

    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )