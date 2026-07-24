from typing import Dict, Any, Optional
from frontend.services.api_client import api_client

class AnalysisService:
    @staticmethod
    def _post_analysis(endpoint: str, resume_id: str, jd_id: Optional[str] = None) -> Dict[str, Any]:
        payload = {"resume_id": resume_id}
        if jd_id:
            payload["jd_id"] = jd_id
        return api_client.post(endpoint, json=payload)

    @staticmethod
    def match_score(resume_id: str, jd_id: str) -> Dict[str, Any]:
        return AnalysisService._post_analysis("/analyze/match", resume_id, jd_id)

    @staticmethod
    def missing_skills(resume_id: str, jd_id: str) -> Dict[str, Any]:
        return AnalysisService._post_analysis("/analyze/skills", resume_id, jd_id)

    @staticmethod
    def ats_analysis(resume_id: str, jd_id: str) -> Dict[str, Any]:
        return AnalysisService._post_analysis("/analyze/ats", resume_id, jd_id)

    @staticmethod
    def interview_questions(resume_id: str, jd_id: str) -> Dict[str, Any]:
        return AnalysisService._post_analysis("/analyze/interview-questions", resume_id, jd_id)

    @staticmethod
    def summary(resume_id: str, jd_id: Optional[str] = None) -> Dict[str, Any]:
        return AnalysisService._post_analysis("/analyze/summary", resume_id, jd_id)
