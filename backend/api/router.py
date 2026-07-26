"""
FastAPI Main Router.

Architectural layer:
    API (Routing).

Purpose:
    Acts as the central mounting point for all sub-routers (documents, chat, health, etc.).
    Keeps the main FastAPI application entrypoint clean.

Related modules:
    - backend.api.*
    - backend.main
"""
from fastapi import APIRouter
from backend.api import documents, chat, health, feedback, analytics, analyze

api_router = APIRouter()
api_router.include_router(documents.router)
api_router.include_router(chat.router)
api_router.include_router(health.router)
api_router.include_router(feedback.router)
api_router.include_router(analytics.router)
api_router.include_router(analyze.router)

@api_router.get("/health")
async def health_check():
    """
    Top-level API health check endpoint.
    """
    return {"status": "ok", "message": "CogniHire API is running"}
