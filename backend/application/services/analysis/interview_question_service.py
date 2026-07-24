from typing import List
from pydantic import BaseModel, Field
from backend.core.interfaces.llm_provider import ILLMProvider
from backend.application.services.analysis.base_analysis_service import BaseAnalysisService
from backend.core.domain.chat import Citation
from backend.core.services.prompt_manager import PromptManager

class InterviewQuestion(BaseModel):
    question: str
    expected_answer_guidance: str
    rationale: str

class InterviewQuestionResponse(BaseModel):
    technical_questions: List[InterviewQuestion]
    behavioral_questions: List[InterviewQuestion]
    project_questions: List[InterviewQuestion]
    explanation: str
    citations: List[str] = Field(default_factory=list)

class InterviewQuestionService(BaseAnalysisService):
    def __init__(self, llm_provider: ILLMProvider, prompt_manager: PromptManager):
        self.llm_provider = llm_provider
        self.prompt_manager = prompt_manager

    async def analyze(self, jd_context: str, resume_context: str, citations: List[Citation]) -> InterviewQuestionResponse:
        system_prompt = self.prompt_manager.get_prompt("interview_questions")

        prompt = f"Job Description Context:\n{jd_context}\n\nResume Context:\n{resume_context}"
        
        response_text = await self.llm_provider.generate(prompt, system_prompt=system_prompt)
        
        result = self._parse_json(response_text, InterviewQuestionResponse)
        result.citations = [c.format() for c in citations]
        
        return result
