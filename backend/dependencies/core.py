"""
Dependency Injection Container (Core).

Architectural layer:
    API (Dependency Injection).

Purpose:
    Acts as the composition root for the application. Wires together concrete
    infrastructure implementations and injects them into application use cases.
    Maintains singleton instances for heavyweight components like models and vector stores.

Data flow:
    FastAPI Depends() -> get_use_case() -> assembles use case using singletons -> returns instance.

Related modules:
    - backend.api.*
"""
from backend.infrastructure.parsers.pdf_parser import PDFDocumentParser
from backend.infrastructure.parsers.docx_parser import DOCXDocumentParser
from backend.infrastructure.classifiers.rule_based_classifier import RuleBasedDocumentClassifier
from backend.infrastructure.parsers.section_parser import RuleBasedSectionParser
from backend.infrastructure.parsers.metadata_extractor import MetadataExtractor
from backend.infrastructure.chunkers.section_chunker import SectionAwareChunker
from backend.infrastructure.embedders.bge_embedder import BGEEmbeddingProvider
from backend.infrastructure.vectorstores.chroma_repository import ChromaIndexRepository
from backend.application.use_cases.ingest_document import IngestDocumentUseCase
from backend.config.settings import settings

# Phase 3B Dependencies
from backend.infrastructure.retrievers.vector_retriever import VectorRetriever
from backend.infrastructure.retrievers.bm25_retriever import BM25Retriever
from backend.infrastructure.retrievers.rrf_retriever import RRFRetriever
from backend.infrastructure.rerankers.bge_reranker import BGEReranker
from backend.infrastructure.llm.gemini_provider import GeminiProvider
from backend.infrastructure.repositories.memory_chat_session_repository import MemoryChatSessionRepository
from backend.application.services.query_rewriter import QueryRewriter
from backend.application.services.context_builder import ContextBuilder
from backend.application.use_cases.chat_pipeline import ChatPipelineUseCase
from backend.core.services.prompt_manager import PromptManager

# Phase 3C Dependencies
from backend.application.services.analysis.match_score_service import MatchScoreService
from backend.application.services.analysis.missing_skills_service import MissingSkillsService
from backend.application.services.analysis.ats_analysis_service import ATSAnalysisService
from backend.application.services.analysis.relevant_experience_service import RelevantExperienceService
from backend.application.services.analysis.interview_question_service import InterviewQuestionService
from backend.application.services.analysis.summary_service import ResumeSummaryService, JDSummaryService
from backend.application.use_cases.hiring_analysis_pipeline import HiringAnalysisUseCase

# Singletons - instantiated once at startup to save memory and avoid model reload costs
_pdf_parser = PDFDocumentParser()
_docx_parser = DOCXDocumentParser()
_classifier = RuleBasedDocumentClassifier()
_section_parser = RuleBasedSectionParser()
_metadata_extractor = MetadataExtractor()
_chunker = SectionAwareChunker()
_embedder = BGEEmbeddingProvider()
_index_repo = ChromaIndexRepository(persist_directory=settings.CHROMADB_DIR, embedder=_embedder)

def get_index_repository() -> ChromaIndexRepository:
    """FastAPI dependency yielding the singleton vector store repository."""
    return _index_repo

def get_ingest_document_use_case() -> IngestDocumentUseCase:
    """FastAPI dependency yielding a configured document ingestion pipeline."""
    return IngestDocumentUseCase(
        pdf_parser=_pdf_parser,
        docx_parser=_docx_parser,
        classifier=_classifier,
        section_parser=_section_parser,
        chunker=_chunker,
        metadata_extractor=_metadata_extractor,
        embedder=_embedder,
        index_repository=_index_repo
    )

_vector_retriever = VectorRetriever(embedder=_embedder, index_repository=_index_repo)
_bm25_retriever = BM25Retriever(index_repository=_index_repo)
_rrf_retriever = RRFRetriever(vector_retriever=_vector_retriever, bm25_retriever=_bm25_retriever)
_bge_reranker = BGEReranker()
_gemini_provider = GeminiProvider()
_chat_session_repo = MemoryChatSessionRepository()
_prompt_manager = PromptManager()
_query_rewriter = QueryRewriter(llm_provider=_gemini_provider, prompt_manager=_prompt_manager)
_context_builder = ContextBuilder()

def get_chat_pipeline_use_case() -> ChatPipelineUseCase:
    """FastAPI dependency yielding a configured conversational RAG pipeline."""
    return ChatPipelineUseCase(
        retriever=_rrf_retriever,
        reranker=_bge_reranker,
        llm_provider=_gemini_provider,
        session_repository=_chat_session_repo,
        query_rewriter=_query_rewriter,
        context_builder=_context_builder,
        prompt_manager=_prompt_manager
    )

_match_score_service = MatchScoreService(llm_provider=_gemini_provider, prompt_manager=_prompt_manager)
_missing_skills_service = MissingSkillsService(llm_provider=_gemini_provider, prompt_manager=_prompt_manager)
_ats_analysis_service = ATSAnalysisService(llm_provider=_gemini_provider, prompt_manager=_prompt_manager)
_relevant_experience_service = RelevantExperienceService(llm_provider=_gemini_provider, prompt_manager=_prompt_manager)
_interview_question_service = InterviewQuestionService(llm_provider=_gemini_provider, prompt_manager=_prompt_manager)
_resume_summary_service = ResumeSummaryService(llm_provider=_gemini_provider, prompt_manager=_prompt_manager)
_jd_summary_service = JDSummaryService(llm_provider=_gemini_provider, prompt_manager=_prompt_manager)

def get_hiring_analysis_use_case() -> HiringAnalysisUseCase:
    """FastAPI dependency yielding a configured structured hiring analysis pipeline."""
    return HiringAnalysisUseCase(
        index_repository=_index_repo,
        context_builder=_context_builder,
        match_score_service=_match_score_service,
        missing_skills_service=_missing_skills_service,
        ats_analysis_service=_ats_analysis_service,
        relevant_experience_service=_relevant_experience_service,
        interview_question_service=_interview_question_service,
        resume_summary_service=_resume_summary_service,
        jd_summary_service=_jd_summary_service
    )
