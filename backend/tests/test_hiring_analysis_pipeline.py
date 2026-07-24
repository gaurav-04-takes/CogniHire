import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.application.use_cases.hiring_analysis_pipeline import HiringAnalysisUseCase

@pytest.fixture
def mock_dependencies():
    index_repo = MagicMock()
    context_builder = MagicMock()
    
    # Return dummy context string and empty citations list
    context_builder.build_context.return_value = ("Dummy Context", [])
    
    match_score = AsyncMock()
    missing_skills = AsyncMock()
    ats_analysis = AsyncMock()
    relevant_exp = AsyncMock()
    interview_q = AsyncMock()
    resume_summary = AsyncMock()
    jd_summary = AsyncMock()
    
    return {
        "index_repository": index_repo,
        "context_builder": context_builder,
        "match_score_service": match_score,
        "missing_skills_service": missing_skills,
        "ats_analysis_service": ats_analysis,
        "relevant_experience_service": relevant_exp,
        "interview_question_service": interview_q,
        "resume_summary_service": resume_summary,
        "jd_summary_service": jd_summary
    }

@pytest.fixture
def pipeline(mock_dependencies):
    return HiringAnalysisUseCase(**mock_dependencies)

@pytest.mark.asyncio
async def test_generate_match_score(pipeline, mock_dependencies):
    await pipeline.generate_match_score("resume1", "jd1")
    
    mock_dependencies["match_score_service"].analyze.assert_called_once_with(
        "Dummy Context", "Dummy Context", []
    )
    assert mock_dependencies["index_repository"].get_chunks.call_count == 2

@pytest.mark.asyncio
async def test_generate_missing_skills(pipeline, mock_dependencies):
    await pipeline.generate_missing_skills("resume1", "jd1")
    mock_dependencies["missing_skills_service"].analyze.assert_called_once()

@pytest.mark.asyncio
async def test_generate_ats_analysis(pipeline, mock_dependencies):
    await pipeline.generate_ats_analysis("resume1", "jd1")
    mock_dependencies["ats_analysis_service"].analyze.assert_called_once()

@pytest.mark.asyncio
async def test_generate_relevant_experience(pipeline, mock_dependencies):
    await pipeline.generate_relevant_experience("resume1", "jd1")
    mock_dependencies["relevant_experience_service"].analyze.assert_called_once()

@pytest.mark.asyncio
async def test_generate_interview_questions(pipeline, mock_dependencies):
    await pipeline.generate_interview_questions("resume1", "jd1")
    mock_dependencies["interview_question_service"].analyze.assert_called_once()

@pytest.mark.asyncio
async def test_generate_resume_summary(pipeline, mock_dependencies):
    await pipeline.generate_resume_summary("resume1")
    mock_dependencies["resume_summary_service"].analyze.assert_called_once_with(
        "Dummy Context", []
    )

@pytest.mark.asyncio
async def test_generate_jd_summary(pipeline, mock_dependencies):
    await pipeline.generate_jd_summary("jd1")
    mock_dependencies["jd_summary_service"].analyze.assert_called_once_with(
        "Dummy Context", []
    )
