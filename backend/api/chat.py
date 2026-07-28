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
from sqlalchemy.orm import Session
from backend.infrastructure.database.session import get_db
from backend.infrastructure.database.models import DocumentModel, DocumentProcessingJobModel, ProcessingStatus
from backend.core.domain.document import DocumentType
from backend.core.domain.exceptions import ValidationError, DocumentNotFoundError, DocumentProcessingError, LLMProviderError

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    resume_document_id: str
    jd_document_id: str
    collection_name: str = "documents"

class ChatResponse(BaseModel):
    response: str
    session_id: str
    citations: list

def validate_documents(db: Session, resume_id: str, jd_id: str):
    if resume_id == jd_id:
        raise ValidationError("Resume and Job Description cannot be the same document.")
        
    resume_doc = db.query(DocumentModel).filter(DocumentModel.id == resume_id).first()
    jd_doc = db.query(DocumentModel).filter(DocumentModel.id == jd_id).first()
    
    if not resume_doc or not jd_doc:
        raise DocumentNotFoundError("One or both selected documents were not found.")
        
    if resume_doc.doc_type != DocumentType.RESUME.value:
        raise ValidationError(f"Document {resume_id} is not classified as a Resume.")
        
    if jd_doc.doc_type != DocumentType.JOB_DESCRIPTION.value:
        raise ValidationError(f"Document {jd_id} is not classified as a Job Description.")
        
    resume_job = db.query(DocumentProcessingJobModel).filter(DocumentProcessingJobModel.document_id == resume_id).first()
    jd_job = db.query(DocumentProcessingJobModel).filter(DocumentProcessingJobModel.document_id == jd_id).first()
    
    if not resume_job or resume_job.status != ProcessingStatus.COMPLETED or not resume_job.indexed:
        raise DocumentProcessingError(f"Resume {resume_id} is not fully processed and indexed.")
        
    if not jd_job or jd_job.status != ProcessingStatus.COMPLETED or not jd_job.indexed:
        raise DocumentProcessingError(f"Job Description {jd_id} is not fully processed and indexed.")

@router.post("")
async def chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    use_case: ChatPipelineUseCase = Depends(get_chat_pipeline_use_case)
):
    """
    Synchronous chat endpoint. Returns the complete response and citations.
    Triggers RAGAS background evaluation asynchronously.
    """
    try:
        validate_documents(db, request.resume_document_id, request.jd_document_id)
        
        response_text, assistant_msg, session = await use_case.execute(
            query=request.query,
            session_id=request.session_id,
            resume_document_id=request.resume_document_id,
            jd_document_id=request.jd_document_id,
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
    except (ValidationError, DocumentNotFoundError, DocumentProcessingError):
        raise
    except Exception as e:
        raise LLMProviderError(str(e))

from fastapi.responses import StreamingResponse

@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    db: Session = Depends(get_db),
    use_case: ChatPipelineUseCase = Depends(get_chat_pipeline_use_case)
):
    """
    Streaming chat endpoint. Yields SSE events as the LLM generates tokens.
    """
    try:
        validate_documents(db, request.resume_document_id, request.jd_document_id)
        
        generator = use_case.execute_stream(
            query=request.query,
            session_id=request.session_id,
            resume_document_id=request.resume_document_id,
            jd_document_id=request.jd_document_id,
            collection_name=request.collection_name
        )
        return StreamingResponse(generator, media_type="text/event-stream")
    except (ValidationError, DocumentNotFoundError, DocumentProcessingError):
        raise
    except Exception as e:
        raise LLMProviderError(str(e))

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
