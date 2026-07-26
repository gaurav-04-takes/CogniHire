"""
Missing Skills Analysis Service.

Architectural layer:
    Application (Service).

Purpose:
    Identifies hard and soft skills required by the JD that are not explicitly
    found in the candidate's resume, assessing the impact of each gap.

Data flow:
    Accepts full document contexts -> Prompts LLM for JSON -> Parses into MissingSkillsResponse.

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

class SkillGap(BaseModel):
    skill: str
    impact: str
    recommendation: str

class MissingSkillsResponse(BaseModel):
    missing_skills: List[SkillGap]
    explanation: str
    citations: List[str] = Field(default_factory=list)

class MissingSkillsService(BaseAnalysisService):
    """
    Analyzes skill gaps between a resume and a JD.
    """
    def __init__(self, llm_provider: ILLMProvider, prompt_manager: PromptManager):
        self.llm_provider = llm_provider
        self.prompt_manager = prompt_manager

    async def analyze(self, jd_context: str, resume_context: str, citations: List[Citation]) -> MissingSkillsResponse:
        """
        Executes the LLM prompt to detect missing skills and parses the JSON output.
        
        Args:
            jd_context: Context string for the JD.
            resume_context: Context string for the resume.
            citations: Source references to append.
            
        Returns:
            A structured MissingSkillsResponse detailing the gaps and impacts.
        """
        system_prompt = self.prompt_manager.get_prompt("missing_skills")

        prompt = f"Job Description Context:\n{jd_context}\n\nResume Context:\n{resume_context}"
        
        response_text = await self.llm_provider.generate(prompt, system_prompt=system_prompt)
        
        result = self._parse_json(response_text, MissingSkillsResponse)
        result.citations = [c.format() for c in citations]
        
        return result
