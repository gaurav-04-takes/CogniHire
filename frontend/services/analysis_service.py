"""
Frontend Analysis Service.

Architectural layer:
    Frontend (Service Abstraction).

Purpose:
    Abstracts API calls to the backend `/analyze` endpoints for fetching
    match scores, missing skills, ATS feedback, and summaries.
"""
from typing import Dict, Any, Optional
from frontend.services.api_client import api_client

class AnalysisService:
    """
    Provides static methods to retrieve AI-generated hiring analyses.
    """
    
    @staticmethod
    def _post_analysis(endpoint: str, resume_id: str, jd_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Helper method to construct and send standard analysis request payloads.
        """
        payload = {"resume_id": resume_id}
        if jd_id:
            payload["jd_id"] = jd_id
        return api_client.post(endpoint, json=payload)

    @staticmethod
    def match_score(resume_id: str, jd_id: str) -> Dict[str, Any]:
        """
        Retrieves the structured Match Score analysis.
        """
        return AnalysisService._post_analysis("/analyze/match", resume_id, jd_id)

    @staticmethod
    def missing_skills(resume_id: str, jd_id: str) -> Dict[str, Any]:
        """
        Retrieves the Missing Skills analysis.
        """
        return AnalysisService._post_analysis("/analyze/skills", resume_id, jd_id)

    @staticmethod
    def ats_analysis(resume_id: str, jd_id: str) -> Dict[str, Any]:
        """
        Retrieves the ATS compatibility analysis.
        """
        return AnalysisService._post_analysis("/analyze/ats", resume_id, jd_id)

    @staticmethod
    def interview_questions(resume_id: str, jd_id: str) -> Dict[str, Any]:
        """
        Retrieves generated Interview Questions based on the candidate's gaps.
        """
        return AnalysisService._post_analysis("/analyze/interview-questions", resume_id, jd_id)

    @staticmethod
    def summary(resume_id: str, jd_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieves executive summaries for the provided documents.
        """
        return AnalysisService._post_analysis("/analyze/summary", resume_id, jd_id)
