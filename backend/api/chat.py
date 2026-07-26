"""
FastAPI Chat Routes.

Architectural layer:
    API (Controllers).

Purpose:
    Exposes endpoints for the conversational RAG interface. Handles synchronous
    chat, streaming chat, and chat history management.

Key dependencies:
    - backend.dependencies.core
    - backend.application.use_cases.chat_pipeline
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from backend.dependencies.core import get_chat_pipeline_use_case, _chat_session_repo
from backend.application.use_cases.chat_pipeline import ChatPipelineUseCase
from backend.core.services.evaluation_service import EvaluationService
from fastapi import BackgroundTasks

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    collection_name: str = "documents"

class ChatResponse(BaseModel):
    response: str
    session_id: str
    citations: list

@router.post("")
async def chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    use_case: ChatPipelineUseCase = Depends(get_chat_pipeline_use_case)
):
    """
    Synchronous chat endpoint. Returns the complete response and citations.
    Triggers RAGAS background evaluation asynchronously.
    """
    try:
        response_text, assistant_msg, session = await use_case.execute(
            query=request.query,
            session_id=request.session_id,
            collection_name=request.collection_name
        )
        
        # Trigger background evaluation
        eval_service = EvaluationService() # In real app, inject db_session
        contexts = [c.format() for c in assistant_msg.citations] if assistant_msg.citations else []
        background_tasks.add_task(
            eval_service.evaluate_response,
            query=request.query,
            answer=response_text,
            contexts=contexts,
            session_id=session.session_id
        )
        
        return ChatResponse(
            response=response_text,
            session_id=session.session_id,
            citations=[c.dict() for c in assistant_msg.citations]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.responses import StreamingResponse

@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    use_case: ChatPipelineUseCase = Depends(get_chat_pipeline_use_case)
):
    """
    Streaming chat endpoint. Yields SSE events as the LLM generates tokens.
    """
    try:
        generator = use_case.execute_stream(
            query=request.query,
            session_id=request.session_id,
            collection_name=request.collection_name
        )
        return StreamingResponse(generator, media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/history")
async def get_history(session_id: str):
    """
    Retrieves the complete message history for a given chat session.
    """
    session = _chat_session_repo.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session.dict()

@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """
    Deletes a chat session from memory/storage.
    """
    session = _chat_session_repo.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    _chat_session_repo.delete(session_id)
    return {"status": "success", "message": f"Session {session_id} deleted."}
