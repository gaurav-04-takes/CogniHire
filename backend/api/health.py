from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.infrastructure.database.session import get_db
from backend.dependencies.core import get_index_repository, get_chat_pipeline_use_case
from backend.core.interfaces.index_repository import IIndexRepository
from backend.application.use_cases.chat_pipeline import ChatPipelineUseCase
from backend.core.services.evaluation_service import EvaluationService
import shutil

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/database")
async def health_database(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "message": "Database is reachable"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/vectorstore")
async def health_vectorstore(index_repo: IIndexRepository = Depends(get_index_repository)):
    try:
        # ChromaDB health check
        # Depending on the client, we can ping or just catch exceptions
        resumes = index_repo.get_chunks("resumes")
        jds = index_repo.get_chunks("job_descriptions")
        return {
            "status": "ok", 
            "message": "Vectorstore is reachable",
            "resumes_chunk_count": len(resumes),
            "jds_chunk_count": len(jds)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/llm")
async def health_llm(chat_use_case: ChatPipelineUseCase = Depends(get_chat_pipeline_use_case)):
    try:
        import time
        from backend.config.settings import settings
        
        if not settings.GEMINI_API_KEY:
            return {"status": "error", "message": "GEMINI_API_KEY is not configured"}
            
        start_time = time.time()
        # Ping Gemini
        response = await chat_use_case.llm_provider.generate("Ping. Reply with exactly 'Pong'.")
        latency_ms = int((time.time() - start_time) * 1000)
        
        if "Pong" in response or "pong" in response.lower():
            return {
                "status": "healthy", 
                "provider": "gemini",
                "model": settings.GEMINI_MODEL,
                "latency_ms": latency_ms
            }
        return {"status": "warning", "message": "LLM returned unexpected response"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/disk")
async def health_disk():
    try:
        total, used, free = shutil.disk_usage("/")
        free_gb = free // (2**30)
        return {
            "status": "ok" if free_gb > 1 else "warning",
            "message": "Disk space checked",
            "free_gb": free_gb
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/evaluation")
async def health_evaluation():
    try:
        eval_service = EvaluationService()
        return {
            "status": "ok",
            "ragas_available": eval_service.ragas_available
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
