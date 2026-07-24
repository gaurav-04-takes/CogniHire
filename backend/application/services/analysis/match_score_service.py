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
    def __init__(self, llm_provider: ILLMProvider, prompt_manager: PromptManager):
        self.llm_provider = llm_provider
        self.prompt_manager = prompt_manager

    async def analyze(self, jd_context: str, resume_context: str, citations: List[Citation]) -> MatchScoreResponse:
        system_prompt = self.prompt_manager.get_prompt("match_score")

        prompt = f"Job Description Context:\n{jd_context}\n\nResume Context:\n{resume_context}"
        
        response_text = await self.llm_provider.generate(prompt, system_prompt=system_prompt)
        
        result = self._parse_json(response_text, MatchScoreResponse)
        
        # Attach formatted citations
        result.citations = [c.format() for c in citations]
        
        return result
