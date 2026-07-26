"""
Hiring Analysis Pipeline Use Case.

Architectural layer:
    Application (Use Case)

Purpose:
    Provides a unified API for generating structured AI analyses between a
    resume and a job description. Coordinates fetching relevant vector contexts
    and delegating the actual generative tasks to specialized services.

Data flow:
    Accepts document IDs -> Retrieves filtered vector chunks via IndexRepository ->
    Builds context string -> Delegates to specific Analysis Services (e.g., MatchScore)
    -> Returns structured Pydantic models.

Key dependencies:
    - backend.core.interfaces.index_repository
    - backend.application.services.context_builder
    - backend.application.services.analysis.*

Side effects:
    - Causes downstream LLM API calls via the analysis services.

Related modules:
    - backend.api.hiring_intelligence
"""
from typing import List, Tuple
from backend.core.interfaces.index_repository import IIndexRepository
from backend.application.services.context_builder import ContextBuilder
from backend.application.services.analysis.match_score_service import MatchScoreService, MatchScoreResponse
from backend.application.services.analysis.missing_skills_service import MissingSkillsService, MissingSkillsResponse
from backend.application.services.analysis.ats_analysis_service import ATSAnalysisService, ATSAnalysisResponse
from backend.application.services.analysis.relevant_experience_service import RelevantExperienceService, RelevantExperienceResponse
from backend.application.services.analysis.interview_question_service import InterviewQuestionService, InterviewQuestionResponse
from backend.application.services.analysis.summary_service import ResumeSummaryService, JDSummaryService, SummaryResponse
from backend.core.domain.chat import Citation

class HiringAnalysisUseCase:
    """
    Coordinator for all AI-driven resume vs JD comparison operations.
    """
    def __init__(
        self,
        index_repository: IIndexRepository,
        context_builder: ContextBuilder,
        match_score_service: MatchScoreService,
        missing_skills_service: MissingSkillsService,
        ats_analysis_service: ATSAnalysisService,
        relevant_experience_service: RelevantExperienceService,
        interview_question_service: InterviewQuestionService,
        resume_summary_service: ResumeSummaryService,
        jd_summary_service: JDSummaryService
    ):
        self.index_repository = index_repository
        self.context_builder = context_builder
        self.match_score_service = match_score_service
        self.missing_skills_service = missing_skills_service
        self.ats_analysis_service = ats_analysis_service
        self.relevant_experience_service = relevant_experience_service
        self.interview_question_service = interview_question_service
        self.resume_summary_service = resume_summary_service
        self.jd_summary_service = jd_summary_service

    def _get_document_context(self, document_id: str, doc_type: str, collection_name: str = "documents") -> Tuple[str, List[Citation]]:
        """
        Retrieves all chunks for a specific document and formats them into an LLM context string.
        
        Args:
            document_id: UUID of the target document.
            doc_type: Either 'resume' or 'job_description' for metadata filtering.
            collection_name: The target vector database collection.
            
        Returns:
            A tuple containing the formatted context string and the list of citations.
        """
        filters = {
            "$and": [
                {"document_id": document_id},
                {"document_type": doc_type}
            ]
        }
        chunks = self.index_repository.get_chunks(collection_name=collection_name, filters=filters)
        return self.context_builder.build_context(chunks)

    async def generate_match_score(self, resume_id: str, jd_id: str) -> MatchScoreResponse:
        """
        Generates a comprehensive match score across multiple dimensions.
        """
        resume_context, resume_citations = self._get_document_context(resume_id, "resume")
        jd_context, jd_citations = self._get_document_context(jd_id, "job_description")
        
        # Combine citations from both, though mostly resume citations are used to ground claims
        return await self.match_score_service.analyze(jd_context, resume_context, resume_citations + jd_citations)

    async def generate_missing_skills(self, resume_id: str, jd_id: str) -> MissingSkillsResponse:
        """
        Identifies critical skills required by the JD that are absent from the resume.
        """
        resume_context, resume_citations = self._get_document_context(resume_id, "resume")
        jd_context, jd_citations = self._get_document_context(jd_id, "job_description")
        
        return await self.missing_skills_service.analyze(jd_context, resume_context, resume_citations + jd_citations)

    async def generate_ats_analysis(self, resume_id: str, jd_id: str) -> ATSAnalysisResponse:
        """
        Provides ATS keyword analysis, highlighting present and missing terms.
        """
        resume_context, resume_citations = self._get_document_context(resume_id, "resume")
        jd_context, jd_citations = self._get_document_context(jd_id, "job_description")
        
        return await self.ats_analysis_service.analyze(jd_context, resume_context, resume_citations + jd_citations)

    async def generate_relevant_experience(self, resume_id: str, jd_id: str) -> RelevantExperienceResponse:
        """
        Extracts and ranks the candidate's past experience snippets against JD requirements.
        """
        resume_context, resume_citations = self._get_document_context(resume_id, "resume")
        jd_context, jd_citations = self._get_document_context(jd_id, "job_description")
        
        return await self.relevant_experience_service.analyze(jd_context, resume_context, resume_citations + jd_citations)

    async def generate_interview_questions(self, resume_id: str, jd_id: str) -> InterviewQuestionResponse:
        """
        Generates tailored interview questions based on the candidate's specific background and JD gaps.
        """
        resume_context, resume_citations = self._get_document_context(resume_id, "resume")
        jd_context, jd_citations = self._get_document_context(jd_id, "job_description")
        
        return await self.interview_question_service.analyze(jd_context, resume_context, resume_citations + jd_citations)

    async def generate_resume_summary(self, resume_id: str) -> SummaryResponse:
        """
        Generates a concise executive summary of a candidate's resume.
        """
        resume_context, resume_citations = self._get_document_context(resume_id, "resume")
        return await self.resume_summary_service.analyze(resume_context, resume_citations)

    async def generate_jd_summary(self, jd_id: str) -> SummaryResponse:
        """
        Generates a concise executive summary of a job description.
        """
        jd_context, jd_citations = self._get_document_context(jd_id, "job_description")
        return await self.jd_summary_service.analyze(jd_context, jd_citations)
