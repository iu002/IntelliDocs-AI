"""FastAPI application entry point for IntelliDocs AI."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import CORS_ORIGINS
from backend.app.routers.chat import router as chat_router
from backend.app.routers.health import router as health_router
from backend.app.routers.index import router as index_router
from backend.app.routers.upload import router as upload_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# FastAPI is a Python framework for building web APIs quickly and easily.
app = FastAPI(
    title="IntelliDocs AI",
    version="1.0.0",
    description="AI Powered RAG Document Assistant",
)

# CORS allows the frontend running on localhost to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the health router for the /health endpoint.
app.include_router(health_router)

# Include the upload router for future document uploads.
app.include_router(upload_router)

# Include the indexing router for document storage.
app.include_router(index_router)

# Include the chat router for question answering.
app.include_router(chat_router)


@app.get("/")
def read_root() -> dict[str, str]:
    """Return a simple welcome message for the home page."""
    logger.info("Root endpoint requested.")
    return {"message": "Welcome to IntelliDocs AI"}


if __name__ == "__main__":
    import uvicorn

    # uvicorn is the server that runs the FastAPI app locally.
    uvicorn.run(app, host="127.0.0.1", port=8000)
