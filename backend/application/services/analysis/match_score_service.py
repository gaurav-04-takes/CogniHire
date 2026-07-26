"""
Match Score Analysis Service.

Architectural layer:
    Application (Service).

Purpose:
    Generates a multi-dimensional fit score comparing a candidate's resume to
    a specific job description. Evaluates skills, experience, education, and keywords.

Data flow:
    Accepts full document contexts -> Prompts LLM for JSON -> Parses into MatchScoreResponse.

Key dependencies:
    - backend.core.interfaces.llm_provider
    - backend.application.services.analysis.base_analysis_service

Related modules:
    - backend.application.use_cases.hiring_analysis_pipeline
"""
from typing import List
from pydantic import BaseModel, Field
from backend.core.interfaces.llm_provider import ILLMProvider
from backend.application.services.analysis.base_analysis_service import BaseAnalysisService
from backend.core.domain.chat import Citation
from backend.core.services.prompt_manager import PromptManager

class MatchDimension(BaseModel):
    score: float = Field(..., description="Score out of 100")
    explanation: str

class MatchScoreResponse(BaseModel):
    overall_score: float = Field(..., description="Overall score out of 100")
    skills: MatchDimension
    experience: MatchDimension
    education: MatchDimension
    keywords: MatchDimension
    explanation: str
    citations: List[str] = Field(default_factory=list)

class MatchScoreService(BaseAnalysisService):
    """
    Evaluates the holistic alignment between a resume and JD.
    """
    def __init__(self, llm_provider: ILLMProvider, prompt_manager: PromptManager):
        self.llm_provider = llm_provider
        self.prompt_manager = prompt_manager

    async def analyze(self, jd_context: str, resume_context: str, citations: List[Citation]) -> MatchScoreResponse:
        """
        Executes the LLM prompt and parses the structural match score response.
        
        Args:
            jd_context: Complete formatted chunks of the job description.
            resume_context: Complete formatted chunks of the candidate resume.
            citations: Origin citations to append to the final response.
            
        Returns:
            A structured MatchScoreResponse model.
        """
        system_prompt = self.prompt_manager.get_prompt("match_score")

        prompt = f"Job Description Context:\n{jd_context}\n\nResume Context:\n{resume_context}"
        
        response_text = await self.llm_provider.generate(prompt, system_prompt=system_prompt)
        
        result = self._parse_json(response_text, MatchScoreResponse)
        
        # Attach formatted citations
        result.citations = [c.format() for c in citations]
        
        return result
