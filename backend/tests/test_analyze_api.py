import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.infrastructure.database.models import DocumentModel, DocumentProcessingJobModel, ProcessingStatus
from backend.infrastructure.database.session import SessionLocal
from backend.dependencies.core import get_hiring_analysis_use_case
from unittest.mock import AsyncMock

client = TestClient(app)

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def setup_docs(db_session):
    r_id = "test-resume-1"
    j_id = "test-jd-1"
    
    db_session.query(DocumentProcessingJobModel).filter(DocumentProcessingJobModel.document_id.in_([r_id, j_id])).delete()
    db_session.query(DocumentModel).filter(DocumentModel.id.in_([r_id, j_id])).delete()
    db_session.commit()
    
    db_session.add(DocumentModel(id=r_id, filename="resume.pdf", file_type="pdf", doc_type="resume"))
    db_session.add(DocumentProcessingJobModel(document_id=r_id, status=ProcessingStatus.COMPLETED, indexed=True))
    
    db_session.add(DocumentModel(id=j_id, filename="jd.pdf", file_type="pdf", doc_type="job_description"))
    db_session.add(DocumentProcessingJobModel(document_id=j_id, status=ProcessingStatus.COMPLETED, indexed=True))
    
    db_session.commit()
    return r_id, j_id

class MockHiringAnalysisUseCase:
    async def generate_match_score(self, resume_id, jd_id):
        class Resp:
            def dict(self): return {"match": "ok"}
        return Resp()
    async def generate_missing_skills(self, resume_id, jd_id):
        class Resp:
            def dict(self): return {"skills": "ok"}
        return Resp()
    async def generate_ats_analysis(self, resume_id, jd_id):
        class Resp:
            def dict(self): return {"ats": "ok"}
        return Resp()
    async def generate_interview_questions(self, resume_id, jd_id):
        class Resp:
            def dict(self): return {"interview": "ok"}
        return Resp()
    async def generate_resume_summary(self, resume_id):
        class Resp:
            def dict(self): return {"summary": "resume"}
        return Resp()
    async def generate_jd_summary(self, jd_id):
        class Resp:
            def dict(self): return {"summary": "jd"}
        return Resp()

@pytest.fixture
def mock_use_case():
    return MockHiringAnalysisUseCase()

@pytest.fixture(autouse=True)
def override_dependencies(mock_use_case):
    app.dependency_overrides[get_hiring_analysis_use_case] = lambda: mock_use_case
    yield
    app.dependency_overrides.clear()

def test_analyze_match_success(db_session, mock_use_case):
    r_id, j_id = setup_docs(db_session)
    response = client.post("/api/v1/analyze/match", json={"resume_id": r_id, "jd_id": j_id})
    assert response.status_code == 200
    assert response.json() == {"match": "ok"}

def test_analyze_missing_skills(db_session, mock_use_case):
    r_id, j_id = setup_docs(db_session)
    response = client.post("/api/v1/analyze/skills", json={"resume_id": r_id, "jd_id": j_id})
    assert response.status_code == 200

def test_analyze_ats(db_session, mock_use_case):
    r_id, j_id = setup_docs(db_session)
    response = client.post("/api/v1/analyze/ats", json={"resume_id": r_id, "jd_id": j_id})
    assert response.status_code == 200

def test_analyze_interview_questions(db_session, mock_use_case):
    r_id, j_id = setup_docs(db_session)
    response = client.post("/api/v1/analyze/interview-questions", json={"resume_id": r_id, "jd_id": j_id})
    assert response.status_code == 200

def test_analyze_summary_both(db_session, mock_use_case):
    r_id, j_id = setup_docs(db_session)
    response = client.post("/api/v1/analyze/summary", json={"resume_id": r_id, "jd_id": j_id})
    assert response.status_code == 200
    assert "resume_summary" in response.json()
    assert "jd_summary" in response.json()

def test_analyze_summary_resume_only(db_session, mock_use_case):
    r_id, _ = setup_docs(db_session)
    response = client.post("/api/v1/analyze/summary", json={"resume_id": r_id})
    assert response.status_code == 200
    assert "resume_summary" in response.json()
    assert "jd_summary" not in response.json()

def test_analyze_validation_errors(db_session):
    r_id, j_id = setup_docs(db_session)
    
    # Missing JD ID when required
    response = client.post("/api/v1/analyze/match", json={"resume_id": r_id})
    assert response.status_code == 400
    
    # Same ID for resume and JD
    response = client.post("/api/v1/analyze/match", json={"resume_id": r_id, "jd_id": r_id})
    assert response.status_code == 400
    
    # Invalid resume ID
    response = client.post("/api/v1/analyze/match", json={"resume_id": "invalid", "jd_id": j_id})
    assert response.status_code == 404
    
    # JD as Resume
    response = client.post("/api/v1/analyze/match", json={"resume_id": j_id, "jd_id": j_id})
    assert response.status_code == 400
