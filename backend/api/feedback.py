"""
FastAPI Feedback Routes.

Architectural layer:
    API (Controllers).

Purpose:
    Exposes endpoints for users to submit qualitative ratings on LLM responses.

Key dependencies:
    - backend.infrastructure.database.models
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from backend.infrastructure.database.session import get_db
from backend.infrastructure.database.models import FeedbackRecord
from backend.core.services.logging_service import logger

router = APIRouter(prefix="/feedback", tags=["feedback"])

class FeedbackRequest(BaseModel):
    session_id: Optional[str] = None
    response_id: Optional[str] = None
    query: Optional[str] = None
    score: int
    comment: Optional[str] = None

class FeedbackResponse(BaseModel):
    id: str
    status: str

@router.post("", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest, db: Session = Depends(get_db)):
    """
    Records a user's 1-5 star rating and optional comments for a specific AI response.
    """
    if request.score < 1 or request.score > 5:
        raise HTTPException(status_code=400, detail="Score must be between 1 and 5")
        
    try:
        record = FeedbackRecord(
            session_id=request.session_id,
            response_id=request.response_id,
            query=request.query,
            score=request.score,
            comment=request.comment
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        
        logger.info(f"Feedback submitted: {record.id} with score {record.score}")
        return FeedbackResponse(id=str(record.id), status="success")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to submit feedback: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("")
async def get_feedback(db: Session = Depends(get_db), limit: int = 50, skip: int = 0):
    """
    Retrieves recent feedback records with pagination.
    """
    records = db.query(FeedbackRecord).order_by(FeedbackRecord.created_at.desc()).offset(skip).limit(limit).all()
    return [{"id": r.id, "score": r.score, "comment": r.comment, "created_at": r.created_at} for r in records]
