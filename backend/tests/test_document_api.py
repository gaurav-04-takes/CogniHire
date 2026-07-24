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

def setup_docs(db_session):
    r_id = "test-doc-1"
    j_id = "test-doc-2"
    
    # Clean up first
    db_session.query(DocumentProcessingJobModel).filter(DocumentProcessingJobModel.document_id.in_([r_id, j_id])).delete()
    db_session.query(DocumentModel).filter(DocumentModel.id.in_([r_id, j_id])).delete()
    db_session.commit()
    
    # Insert docs
    db_session.add(DocumentModel(id=r_id, filename="resume.pdf", file_type="pdf", doc_type="resume"))
    db_session.add(DocumentProcessingJobModel(document_id=r_id, status=ProcessingStatus.COMPLETED, indexed=True))
    
    db_session.add(DocumentModel(id=j_id, filename="jd.pdf", file_type="pdf", doc_type="job_description"))
    db_session.add(DocumentProcessingJobModel(document_id=j_id, status=ProcessingStatus.PENDING, indexed=False))
    
    db_session.commit()
    return r_id, j_id

def test_get_documents_api_contract(db_session):
    setup_docs(db_session)
    response = client.get("/api/v1/documents")
    assert response.status_code == 200
    
    data = response.json()
    assert "documents" in data
    assert "total" in data
    
    docs = data["documents"]
    
    # Verify canonical representation and fields
    resume = next(d for d in docs if d["filename"] == "resume.pdf")
    assert resume["document_type"] == "resume"
    assert resume["status"] == "completed"
    assert resume["indexed"] is True
    
    jd = next(d for d in docs if d["filename"] == "jd.pdf")
    assert jd["document_type"] == "job_description"
    assert jd["status"] == "pending"
    assert jd["indexed"] is False

def test_upload_with_override(db_session, monkeypatch):
    import io
    # We mock the background task to not actually run the heavy pipeline
    mock_background = lambda *args, **kwargs: None
    monkeypatch.setattr("backend.api.documents.BackgroundTasks.add_task", mock_background)
    
    file_content = b"fake pdf content"
    files = {"file": ("test_resume.pdf", io.BytesIO(file_content), "application/pdf")}
    data = {"document_type": "job_description"} # override
    
    response = client.post("/api/v1/documents/upload", files=files, data=data)
    assert response.status_code == 200
    doc_id = response.json()["document_id"]
    
    doc = db_session.query(DocumentModel).filter(DocumentModel.id == doc_id).first()
    assert doc is not None

def test_reclassify_document(db_session, monkeypatch):
    r_id, _ = setup_docs(db_session)
    
    mock_background = lambda *args, **kwargs: None
    monkeypatch.setattr("backend.api.documents.BackgroundTasks.add_task", mock_background)
    
    # We also need to mock open() in reclassify since the file won't exist
    from unittest.mock import mock_open
    import builtins
    m = mock_open(read_data=b"fake data")
    monkeypatch.setattr(builtins, "open", m)
    
    monkeypatch.setattr("os.path.exists", lambda x: True)
    
    response = client.post(f"/api/v1/documents/{r_id}/reclassify", json={"document_type": "job_description"})
    assert response.status_code == 200
    
    job = db_session.query(DocumentProcessingJobModel).filter(DocumentProcessingJobModel.document_id == r_id).first()
    assert job.status == ProcessingStatus.PENDING
    assert job.indexed is False

def test_get_document(db_session):
    r_id, _ = setup_docs(db_session)
    response = client.get(f"/api/v1/documents/{r_id}")
    assert response.status_code == 200
    assert response.json()["id"] == r_id
    
    response = client.get("/api/v1/documents/invalid")
    assert response.status_code == 404

def test_get_document_status(db_session):
    r_id, _ = setup_docs(db_session)
    response = client.get(f"/api/v1/documents/{r_id}/status")
    assert response.status_code == 200
    assert response.json()["document_id"] == r_id
    
    response = client.get("/api/v1/documents/invalid/status")
    assert response.status_code == 404

def test_delete_document(db_session, monkeypatch):
    r_id, _ = setup_docs(db_session)
    
    # mock index repo in dependency injection
    from unittest.mock import MagicMock
    mock_repo = MagicMock()
    app.dependency_overrides["backend.dependencies.core.get_index_repository"] = lambda: mock_repo
    
    response = client.delete(f"/api/v1/documents/{r_id}")
    assert response.status_code == 200
    
    doc = db_session.query(DocumentModel).filter(DocumentModel.id == r_id).first()
    assert doc is None
    
    response = client.delete("/api/v1/documents/invalid")
    assert response.status_code == 404
    
    app.dependency_overrides.clear()

def test_reclassify_document_errors(db_session, monkeypatch):
    r_id, _ = setup_docs(db_session)
    
    # 404
    response = client.post("/api/v1/documents/invalid/reclassify", json={"document_type": "job_description"})
    assert response.status_code == 404
    
    # Invalid doc type
    response = client.post(f"/api/v1/documents/{r_id}/reclassify", json={"document_type": "invalid_type"})
    assert response.status_code == 400
    
    # File not found
    monkeypatch.setattr("os.path.exists", lambda x: False)
    response = client.post(f"/api/v1/documents/{r_id}/reclassify", json={"document_type": "job_description"})
    assert response.status_code == 500

def test_process_document_background(db_session):
    from backend.api.documents import process_document_background
    from backend.core.domain.document import DocumentType
    from unittest.mock import MagicMock
    
    r_id, _ = setup_docs(db_session)
    mock_use_case = MagicMock()
    mock_use_case.execute.return_value = (5, DocumentType.RESUME, {"confidence": 0.99})
    
    process_document_background(
        doc_id=r_id,
        content=b"test",
        filename="test.pdf",
        file_type="pdf",
        use_case=mock_use_case
    )
    
    job = db_session.query(DocumentProcessingJobModel).filter(DocumentProcessingJobModel.document_id == r_id).first()
    assert job.status == ProcessingStatus.COMPLETED
    assert job.chunks_count == 5
    assert job.indexed is True

def test_process_document_background_unknown(db_session):
    from backend.api.documents import process_document_background
    from backend.core.domain.document import DocumentType
    from unittest.mock import MagicMock
    
    r_id, _ = setup_docs(db_session)
    mock_use_case = MagicMock()
    mock_use_case.execute.return_value = (0, DocumentType.UNKNOWN, {"confidence": 0.1})
    
    process_document_background(
        doc_id=r_id,
        content=b"test",
        filename="test.pdf",
        file_type="pdf",
        use_case=mock_use_case
    )
    
    job = db_session.query(DocumentProcessingJobModel).filter(DocumentProcessingJobModel.document_id == r_id).first()
    assert job.status == ProcessingStatus.COMPLETED
    assert job.indexed is False

def test_process_document_background_error(db_session):
    from backend.api.documents import process_document_background
    from unittest.mock import MagicMock
    
    r_id, _ = setup_docs(db_session)
    mock_use_case = MagicMock()
    mock_use_case.execute.side_effect = Exception("Test error")
    
    process_document_background(
        doc_id=r_id,
        content=b"test",
        filename="test.pdf",
        file_type="pdf",
        use_case=mock_use_case
    )
    
    job = db_session.query(DocumentProcessingJobModel).filter(DocumentProcessingJobModel.document_id == r_id).first()
    assert job.status == ProcessingStatus.FAILED
    assert job.error_message == "Test error"

def test_upload_invalid_extension(db_session):
    import io
    file_content = b"fake txt content"
    files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
    
    response = client.post("/api/v1/documents/upload", files=files, data={"document_type": "auto"})
    assert response.status_code == 400
    assert "Only PDF and DOCX files are supported" in response.json()["detail"]
