"""Application configuration settings for the backend."""

from typing import List


# Allow the frontend development server to access the API.
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
]
