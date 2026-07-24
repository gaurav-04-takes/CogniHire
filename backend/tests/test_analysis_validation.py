import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.infrastructure.database.models import DocumentModel, DocumentProcessingJobModel, ProcessingStatus
from backend.infrastructure.database.session import SessionLocal

client = TestClient(app)

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def setup_docs(db_session, r_status, r_type, j_status, j_type, r_indexed=True, j_indexed=True):
    r_id = "test-resume-1"
    j_id = "test-jd-1"
    
    # Clean up first
    db_session.query(DocumentProcessingJobModel).filter(DocumentProcessingJobModel.document_id.in_([r_id, j_id])).delete()
    db_session.query(DocumentModel).filter(DocumentModel.id.in_([r_id, j_id])).delete()
    db_session.commit()
    
    # Insert docs
    if r_type:
        db_session.add(DocumentModel(id=r_id, filename="r.pdf", file_type="pdf", doc_type=r_type))
        db_session.add(DocumentProcessingJobModel(document_id=r_id, status=r_status, indexed=r_indexed))
    if j_type:
        db_session.add(DocumentModel(id=j_id, filename="j.pdf", file_type="pdf", doc_type=j_type))
        db_session.add(DocumentProcessingJobModel(document_id=j_id, status=j_status, indexed=j_indexed))
    
    db_session.commit()
    return r_id, j_id

def test_rejection_missing_resume(db_session):
    response = client.post("/api/v1/analyze/match", json={"resume_id": "nonexistent", "jd_id": "nonexistent"})
    assert response.status_code == 400
    assert "Resume not found" in response.json()["detail"]

def test_rejection_resume_points_to_jd(db_session):
    r_id, j_id = setup_docs(db_session, ProcessingStatus.COMPLETED, "job_description", ProcessingStatus.COMPLETED, "job_description")
    response = client.post("/api/v1/analyze/match", json={"resume_id": r_id, "jd_id": j_id})
    assert response.status_code == 400
    assert "is not a resume" in response.json()["detail"]

def test_rejection_jd_points_to_resume(db_session):
    r_id, j_id = setup_docs(db_session, ProcessingStatus.COMPLETED, "resume", ProcessingStatus.COMPLETED, "resume")
    response = client.post("/api/v1/analyze/match", json={"resume_id": r_id, "jd_id": j_id})
    assert response.status_code == 400
    assert "is not a job description" in response.json()["detail"]

def test_rejection_unindexed_docs(db_session):
    r_id, j_id = setup_docs(db_session, ProcessingStatus.COMPLETED, "resume", ProcessingStatus.COMPLETED, "job_description", r_indexed=False)
    response = client.post("/api/v1/analyze/match", json={"resume_id": r_id, "jd_id": j_id})
    assert response.status_code == 400
    assert "Resume is not fully processed and indexed" in response.json()["detail"]
