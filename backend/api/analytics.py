"""
FastAPI Analytics Routes.

Architectural layer:
    API (Controllers).

Purpose:
    Exposes aggregated system metrics and evaluation results for dashboards.

Key dependencies:
    - backend.infrastructure.database.models
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.infrastructure.database.session import get_db
from backend.infrastructure.database.models import EvaluationResult, FeedbackRecord, SystemMetric

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/metrics")
async def get_metrics(db: Session = Depends(get_db)):
    """
    Computes and returns high-level system averages (feedback, RAGAS scores, latency).
    """
    # Calculate average feedback score
    avg_feedback = db.query(func.avg(FeedbackRecord.score)).scalar() or 0.0
    
    # Calculate evaluation averages
    avg_faithfulness = db.query(func.avg(EvaluationResult.faithfulness_score)).scalar() or 0.0
    avg_relevancy = db.query(func.avg(EvaluationResult.answer_relevancy_score)).scalar() or 0.0
    
    # Fetch recent latency (example)
    latencies = db.query(SystemMetric).filter(SystemMetric.metric_name == "retrieval_latency").order_by(SystemMetric.created_at.desc()).limit(10).all()
    avg_latency = sum(l.metric_value for l in latencies) / len(latencies) if latencies else 0.0
    
    return {
        "average_feedback_score": round(avg_feedback, 2),
        "average_faithfulness": round(avg_faithfulness, 2),
        "average_answer_relevancy": round(avg_relevancy, 2),
        "recent_retrieval_latency_ms": round(avg_latency, 2)
    }
