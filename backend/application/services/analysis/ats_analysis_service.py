"""
ATS Keyword Analysis Service.

Architectural layer:
    Application (Service).

Purpose:
    Extracts critical Applicant Tracking System (ATS) keywords from the JD and 
    checks for their presence or absence in the candidate's resume.

Data flow:
    Accepts document contexts -> Prompts LLM -> Parses into ATSAnalysisResponse.

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

class ATSAnalysisResponse(BaseModel):
    required_keywords: List[str]
    present_keywords: List[str]
    missing_keywords: List[str]
    recommendations: List[str]
    explanation: str
    citations: List[str] = Field(default_factory=list)

class ATSAnalysisService(BaseAnalysisService):
    """
    Analyzes resume keyword optimization against the JD.
    """
    def __init__(self, llm_provider: ILLMProvider, prompt_manager: PromptManager):
        self.llm_provider = llm_provider
        self.prompt_manager = prompt_manager

    async def analyze(self, jd_context: str, resume_context: str, citations: List[Citation]) -> ATSAnalysisResponse:
        """
        Executes the LLM prompt to perform ATS keyword analysis and parses the output.
        
        Args:
            jd_context: Formatted JD chunks.
            resume_context: Formatted resume chunks.
            citations: Context citations to append.
            
        Returns:
            A structured ATSAnalysisResponse.
        """
        system_prompt = self.prompt_manager.get_prompt("ats_analysis")

        prompt = f"Job Description Context:\n{jd_context}\n\nResume Context:\n{resume_context}"
        
        response_text = await self.llm_provider.generate(prompt, system_prompt=system_prompt)
        
        result = self._parse_json(response_text, ATSAnalysisResponse)
        result.citations = [c.format() for c in citations]
        
        return result
