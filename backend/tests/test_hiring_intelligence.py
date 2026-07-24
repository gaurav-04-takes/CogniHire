import pytest
import json
from typing import AsyncGenerator, List, Optional
from backend.core.domain.chat import Citation
from backend.core.interfaces.llm_provider import ILLMProvider
from backend.application.services.analysis.match_score_service import MatchScoreService
from backend.application.services.analysis.missing_skills_service import MissingSkillsService
from backend.application.services.analysis.ats_analysis_service import ATSAnalysisService
from backend.application.services.analysis.relevant_experience_service import RelevantExperienceService
from backend.application.services.analysis.interview_question_service import InterviewQuestionService
from backend.application.services.analysis.summary_service import ResumeSummaryService, JDSummaryService

class MockAnalysisLLMProvider(ILLMProvider):
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        # Match Score
        if "MatchScoreResponse" in system_prompt or "Skills (40%)" in system_prompt:
            return json.dumps({
                "skills": {"score": 90, "explanation": "Good skills"},
                "experience": {"score": 80, "explanation": "Good exp"},
                "education": {"score": 100, "explanation": "Good edu"},
                "keywords": {"score": 70, "explanation": "Good kw"},
                "overall_score": 85.5,
                "explanation": "Overall good match"
            })
        
        # Missing Skills
        if "MissingSkillsResponse" in system_prompt or "missing skills" in system_prompt.lower():
            return json.dumps({
                "missing_skills": [{"skill": "Python", "impact": "High", "recommendation": "Learn it"}],
                "explanation": "One skill missing."
            })
            
        # ATS Analysis
        if "ATSAnalysisResponse" in system_prompt or "Applicant Tracking System" in system_prompt:
            return json.dumps({
                "required_keywords": ["A", "B"],
                "present_keywords": ["A"],
                "missing_keywords": ["B"],
                "recommendations": ["Add B"],
                "explanation": "ATS score ok"
            })
            
        # Relevant Experience
        if "RelevantExperienceResponse" in system_prompt or "rank the experience sections" in system_prompt:
            return json.dumps({
                "ranked_experiences": [
                    {
                        "experience_snippet": "Did a thing",
                        "alignment_explanation": "Aligns well",
                        "rank": 1
                    }
                ],
                "overall_explanation": "Great exp"
            })
            
        # Interview Questions
        if "InterviewQuestionResponse" in system_prompt or "expert technical interviewer" in system_prompt:
            return json.dumps({
                "technical_questions": [{"question": "Q1", "expected_answer_guidance": "A1", "rationale": "R1"}],
                "behavioral_questions": [],
                "project_questions": [],
                "explanation": "Good questions"
            })
            
        # Summary
        if "SummaryResponse" in system_prompt or "overview" in system_prompt:
            return json.dumps({
                "summary": "This is a summary.",
                "key_points": ["Point 1"]
            })

        return "{}"

    async def stream(self, prompt: str, system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        yield "{}"

    async def chat(self, messages: List[any]) -> any:
        pass

@pytest.fixture
def mock_llm():
    return MockAnalysisLLMProvider()

class MockPromptManager:
    def get_prompt(self, prompt_key: str, **kwargs) -> str:
        # Map prompt keys to strings that MockAnalysisLLMProvider expects
        if prompt_key == "match_score": return "MatchScoreResponse"
        if prompt_key == "missing_skills": return "MissingSkillsResponse"
        if prompt_key == "ats_analysis": return "ATSAnalysisResponse"
        if prompt_key == "relevant_experience": return "RelevantExperienceResponse"
        if prompt_key == "interview_questions": return "InterviewQuestionResponse"
        if prompt_key in ["summary_resume", "summary_jd"]: return "SummaryResponse"
        return f"Mock prompt for {prompt_key}"

@pytest.fixture
def mock_prompt_manager():
    return MockPromptManager()

@pytest.fixture
def citations():
    return [Citation(document_id="doc1", document_type="resume", section_type="experience", chunk_index=1)]

@pytest.mark.asyncio
async def test_match_score_service(mock_llm, mock_prompt_manager, citations):
    service = MatchScoreService(mock_llm, mock_prompt_manager)
    result = await service.analyze("JD", "RESUME", citations)
    
    assert result.overall_score == 85.5
    assert result.skills.score == 90
    assert len(result.citations) == 1
    assert "Resume | Experience | Chunk 1" in result.citations[0]

@pytest.mark.asyncio
async def test_missing_skills_service(mock_llm, mock_prompt_manager, citations):
    service = MissingSkillsService(mock_llm, mock_prompt_manager)
    result = await service.analyze("JD", "RESUME", citations)
    
    assert len(result.missing_skills) == 1
    assert result.missing_skills[0].skill == "Python"
    assert len(result.citations) == 1

@pytest.mark.asyncio
async def test_ats_analysis_service(mock_llm, mock_prompt_manager, citations):
    service = ATSAnalysisService(mock_llm, mock_prompt_manager)
    result = await service.analyze("JD", "RESUME", citations)
    
    assert len(result.missing_keywords) == 1
    assert result.missing_keywords[0] == "B"
    assert len(result.citations) == 1

@pytest.mark.asyncio
async def test_relevant_experience_service(mock_llm, mock_prompt_manager, citations):
    service = RelevantExperienceService(mock_llm, mock_prompt_manager)
    result = await service.analyze("JD", "RESUME", citations)
    
    assert len(result.ranked_experiences) == 1
    assert result.ranked_experiences[0].rank == 1
    assert len(result.citations) == 1

@pytest.mark.asyncio
async def test_interview_question_service(mock_llm, mock_prompt_manager, citations):
    service = InterviewQuestionService(mock_llm, mock_prompt_manager)
    result = await service.analyze("JD", "RESUME", citations)
    
    assert len(result.technical_questions) == 1
    assert result.technical_questions[0].question == "Q1"
    assert len(result.citations) == 1

@pytest.mark.asyncio
async def test_summary_services(mock_llm, mock_prompt_manager, citations):
    resume_service = ResumeSummaryService(mock_llm, mock_prompt_manager)
    jd_service = JDSummaryService(mock_llm, mock_prompt_manager)
    
    res = await resume_service.analyze("RESUME", citations)
    jd_res = await jd_service.analyze("JD", citations)
    
    assert res.summary == "This is a summary."
    assert jd_res.summary == "This is a summary."
    assert len(res.citations) == 1
    assert len(jd_res.citations) == 1
