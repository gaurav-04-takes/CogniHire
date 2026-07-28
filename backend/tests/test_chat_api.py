import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from backend.main import app
from backend.dependencies.core import get_chat_pipeline_use_case, _chat_session_repo
from backend.core.domain.chat import ChatSession, ChatMessage, Citation
from backend.api.chat import validate_documents
from backend.core.domain.exceptions import ValidationError, DocumentNotFoundError, DocumentProcessingError
from backend.core.domain.document import DocumentType
from backend.infrastructure.database.models import ProcessingStatus

client = TestClient(app)

class MockChatPipelineUseCase:
    async def execute(self, query, session_id, resume_document_id, jd_document_id, collection_name):
        session = ChatSession(session_id="session_123")
        msg = ChatMessage(role="assistant", content="Response", citations=[
            Citation(document_id="doc1", document_type="resume", section_type="exp", chunk_index=0)
        ])
        return "Response", msg, session

    async def execute_stream(self, query, session_id, resume_document_id, jd_document_id, collection_name):
        yield "Stream "
        yield "Response"

@pytest.fixture
def mock_use_case():
    return MockChatPipelineUseCase()

@pytest.fixture(autouse=True)
def override_dependencies(mock_use_case):
    app.dependency_overrides[get_chat_pipeline_use_case] = lambda: mock_use_case
    yield
    app.dependency_overrides.clear()

def test_chat_endpoint(mock_use_case):
    with patch("backend.api.chat.validate_documents") as mock_validate, patch("backend.api.chat.EvaluationService") as mock_eval:
        response = client.post("/api/v1/chat", json={
            "query": "hello", 
            "session_id": "session_123",
            "resume_document_id": "res_1",
            "jd_document_id": "jd_1"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Response"
        assert data["session_id"] == "session_123"
        assert len(data["citations"]) == 1

def test_chat_endpoint_error(mock_use_case, monkeypatch):
    async def mock_execute(*args, **kwargs):
        raise Exception("Pipeline error")
    monkeypatch.setattr(mock_use_case, "execute", mock_execute)
    with patch("backend.api.chat.validate_documents"):
        response = client.post("/api/v1/chat", json={
            "query": "hello",
            "resume_document_id": "res_1",
            "jd_document_id": "jd_1"
        })
        assert response.status_code == 500

def test_chat_stream_endpoint(mock_use_case):
    with patch("backend.api.chat.validate_documents"):
        response = client.post("/api/v1/chat/stream", json={
            "query": "hello",
            "resume_document_id": "res_1",
            "jd_document_id": "jd_1"
        })
        assert response.status_code == 200

def test_chat_stream_error(mock_use_case, monkeypatch):
    def mock_execute_stream(*args, **kwargs):
        raise Exception("Stream error")
    monkeypatch.setattr(mock_use_case, "execute_stream", mock_execute_stream)
    with patch("backend.api.chat.validate_documents"):
        response = client.post("/api/v1/chat/stream", json={
            "query": "hello",
            "resume_document_id": "res_1",
            "jd_document_id": "jd_1"
        })
        assert response.status_code == 500

def test_validate_documents_same_id():
    mock_db = MagicMock()
    with pytest.raises(ValidationError) as excinfo:
        validate_documents(mock_db, "id1", "id1")
    assert "cannot be the same document" in str(excinfo.value.message)

def test_validate_documents_not_found():
    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = None
    with pytest.raises(DocumentNotFoundError) as excinfo:
        validate_documents(mock_db, "res_1", "jd_1")
    assert "were not found" in str(excinfo.value.message)

def test_validate_documents_wrong_types():
    mock_db = MagicMock()
    mock_resume = MagicMock(doc_type=DocumentType.JOB_DESCRIPTION.value)
    mock_jd = MagicMock(doc_type=DocumentType.RESUME.value)
    
    mock_db.query().filter().first.side_effect = [mock_resume, mock_jd]
    
    with pytest.raises(ValidationError) as excinfo:
        validate_documents(mock_db, "res_1", "jd_1")
    assert "is not classified as a Resume" in str(excinfo.value.message)

def test_validate_documents_unindexed():
    mock_db = MagicMock()
    mock_resume = MagicMock(doc_type=DocumentType.RESUME.value)
    mock_jd = MagicMock(doc_type=DocumentType.JOB_DESCRIPTION.value)
    mock_job = MagicMock(status=ProcessingStatus.PENDING, indexed=False)
    
    mock_db.query().filter().first.side_effect = [mock_resume, mock_jd, mock_job, mock_job]
    
    with pytest.raises(DocumentProcessingError) as excinfo:
        validate_documents(mock_db, "res_1", "jd_1")
    assert "not fully processed and indexed" in str(excinfo.value.message)
