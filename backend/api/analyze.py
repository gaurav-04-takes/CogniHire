"""
FastAPI Analysis Routes.

Architectural layer:
    API (Controllers).

Purpose:
    Exposes endpoints for generating structured AI analyses comparing resumes
    and job descriptions (match scores, missing skills, ATS, etc.).

Key dependencies:
    - backend.dependencies.core
    - backend.application.use_cases.hiring_analysis_pipeline
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.dependencies.core import get_hiring_analysis_use_case
from backend.application.use_cases.hiring_analysis_pipeline import HiringAnalysisUseCase

from sqlalchemy.orm import Session
from backend.infrastructure.database.session import get_db
from backend.infrastructure.database.models import DocumentModel, DocumentProcessingJobModel, ProcessingStatus

router = APIRouter(prefix="/analyze", tags=["analyze"])

class AnalysisRequest(BaseModel):
    resume_id: str
    jd_id: Optional[str] = None

def validate_analysis_docs(request: AnalysisRequest, db: Session = Depends(get_db)):
    """
    FastAPI dependency that validates the requested documents exist, are fully processed,
    and are of the correct expected types (resume vs job_description).
    """
    if request.resume_id:
        resume_doc = db.query(DocumentModel).filter(DocumentModel.id == request.resume_id).first()
        resume_job = db.query(DocumentProcessingJobModel).filter(DocumentProcessingJobModel.document_id == request.resume_id).first()
        if not resume_doc or not resume_job:
            raise HTTPException(status_code=400, detail="Resume not found")
        if resume_doc.doc_type != "resume":
            raise HTTPException(status_code=400, detail="Provided resume_id is not a resume")
        if resume_job.status != ProcessingStatus.COMPLETED or not resume_job.indexed:
            raise HTTPException(status_code=400, detail="Resume is not fully processed and indexed")
            
    if request.jd_id:
        jd_doc = db.query(DocumentModel).filter(DocumentModel.id == request.jd_id).first()
        jd_job = db.query(DocumentProcessingJobModel).filter(DocumentProcessingJobModel.document_id == request.jd_id).first()
        if not jd_doc or not jd_job:
            raise HTTPException(status_code=400, detail="Job description not found")
        if jd_doc.doc_type != "job_description":
            raise HTTPException(status_code=400, detail="Provided jd_id is not a job description")
        if jd_job.status != ProcessingStatus.COMPLETED or not jd_job.indexed:
            raise HTTPException(status_code=400, detail="Job description is not fully processed and indexed")
            
    if request.resume_id and request.jd_id and request.resume_id == request.jd_id:
        raise HTTPException(status_code=400, detail="resume_id and jd_id cannot be the same document")
        
    return request

@router.post("/match")
async def match_score(
    request: AnalysisRequest = Depends(validate_analysis_docs),
    use_case: HiringAnalysisUseCase = Depends(get_hiring_analysis_use_case)
):
    """
    Generates a structured match score evaluating the resume against the JD.
    """
    if not request.jd_id:
        raise HTTPException(status_code=400, detail="jd_id is required for match analysis")
    try:
        response = await use_case.generate_match_score(request.resume_id, request.jd_id)
        return response.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/skills")
async def missing_skills(
    request: AnalysisRequest = Depends(validate_analysis_docs),
    use_case: HiringAnalysisUseCase = Depends(get_hiring_analysis_use_case)
):
    """
    Identifies missing skills in the resume based on JD requirements.
    """
    if not request.jd_id:
        raise HTTPException(status_code=400, detail="jd_id is required for skills analysis")
    try:
        response = await use_case.generate_missing_skills(request.resume_id, request.jd_id)
        return response.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ats")
async def ats_analysis(
    request: AnalysisRequest = Depends(validate_analysis_docs),
    use_case: HiringAnalysisUseCase = Depends(get_hiring_analysis_use_case)
):
    """
    Analyzes ATS keyword presence and absence between the resume and JD.
    """
    if not request.jd_id:
        raise HTTPException(status_code=400, detail="jd_id is required for ATS analysis")
    try:
        response = await use_case.generate_ats_analysis(request.resume_id, request.jd_id)
        return response.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/interview-questions")
async def interview_questions(
    request: AnalysisRequest = Depends(validate_analysis_docs),
    use_case: HiringAnalysisUseCase = Depends(get_hiring_analysis_use_case)
):
    """
    Generates customized interview questions to probe candidate experience and gaps.
    """
    if not request.jd_id:
        raise HTTPException(status_code=400, detail="jd_id is required for interview questions")
    try:
        response = await use_case.generate_interview_questions(request.resume_id, request.jd_id)
        return response.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/summary")
async def summary(
    request: AnalysisRequest = Depends(validate_analysis_docs),
    use_case: HiringAnalysisUseCase = Depends(get_hiring_analysis_use_case)
):
    """
    Generates standalone executive summaries of the provided documents.
    """
    try:
        if request.jd_id:
            # If JD ID is provided, summarize both
            resume_summary = await use_case.generate_resume_summary(request.resume_id)
            jd_summary = await use_case.generate_jd_summary(request.jd_id)
            return {
                "resume_summary": resume_summary.dict(),
                "jd_summary": jd_summary.dict()
            }
        else:
            # Just summarize resume
            resume_summary = await use_case.generate_resume_summary(request.resume_id)
            return {"resume_summary": resume_summary.dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
