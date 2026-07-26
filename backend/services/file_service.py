"""Service helpers for validating and saving uploaded documents."""

import logging
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from backend.utils.file_utils import format_file_size, is_supported_extension

logger = logging.getLogger(__name__)
UPLOAD_DIRECTORY: Path = Path(__file__).resolve().parent.parent / "uploads"
MAX_FILE_SIZE_BYTES: int = 20 * 1024 * 1024

UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)


def ensure_upload_directory() -> Path:
    """Create the upload directory if it does not already exist."""
    UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)
    logger.info("Upload directory ready at %s", UPLOAD_DIRECTORY)
    return UPLOAD_DIRECTORY


async def save_uploaded_file(file: UploadFile) -> dict[str, Any]:
    """Validate an uploaded file, save it, and return its metadata."""
    if file.filename is None or not file.filename.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A file name is required.",
        )

    if not is_supported_extension(file.filename):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type. Only PDF, DOCX, and TXT files are allowed.",
        )

    file_bytes: bytes = await file.read()
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty.",
        )

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the maximum allowed size of {format_file_size(MAX_FILE_SIZE_BYTES)}.",
        )

    upload_directory: Path = ensure_upload_directory()
    file_extension: str = Path(file.filename).suffix.lower()
    unique_filename: str = f"{uuid4().hex}{file_extension}"
    destination_path: Path = upload_directory / unique_filename

    try:
        with destination_path.open("wb") as destination_file:
            destination_file.write(file_bytes)
    except OSError as exc:
        logger.exception("Failed to save uploaded file: %s", file.filename)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The file could not be saved. Please try again.",
        ) from exc

    logger.info("Saved uploaded file as %s", unique_filename)
    return {
        "filename": unique_filename,
        "original_filename": file.filename,
        "file_type": file_extension.lstrip("."),
        "file_size": format_file_size(len(file_bytes)),
        "message": "Upload successful",
    }
