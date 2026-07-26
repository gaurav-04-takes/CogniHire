"""
Relevant Experience Analysis Service.

Architectural layer:
    Application (Service).

Purpose:
    Extracts specific snippets of a candidate's past work history that most closely
    align with the requirements of the job description, ranking them by relevance.

Data flow:
    Accepts contexts -> Prompts LLM -> Parses into RelevantExperienceResponse.

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

class RankedExperience(BaseModel):
    experience_snippet: str
    alignment_explanation: str
    rank: int

class RelevantExperienceResponse(BaseModel):
    ranked_experiences: List[RankedExperience]
    overall_explanation: str
    citations: List[str] = Field(default_factory=list)

class RelevantExperienceService(BaseAnalysisService):
    """
    Identifies and ranks a candidate's most relevant past experiences.
    """
    def __init__(self, llm_provider: ILLMProvider, prompt_manager: PromptManager):
        self.llm_provider = llm_provider
        self.prompt_manager = prompt_manager

    async def analyze(self, jd_context: str, resume_context: str, citations: List[Citation]) -> RelevantExperienceResponse:
        """
        Executes the LLM prompt to extract relevant experiences and parses the JSON.
        
        Args:
            jd_context: JD text chunks.
            resume_context: Resume text chunks.
            citations: Source citations.
            
        Returns:
            A RelevantExperienceResponse containing ranked experiences.
        """
        system_prompt = self.prompt_manager.get_prompt("relevant_experience")

        prompt = f"Job Description Context:\n{jd_context}\n\nResume Context:\n{resume_context}"
        
        response_text = await self.llm_provider.generate(prompt, system_prompt=system_prompt)
        
        result = self._parse_json(response_text, RelevantExperienceResponse)
        result.citations = [c.format() for c in citations]
        
        return result
