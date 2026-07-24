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
    return {"status": "ok", "message": "CogniHire API is running"}
