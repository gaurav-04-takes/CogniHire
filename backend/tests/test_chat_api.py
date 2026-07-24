import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from backend.main import app
from backend.dependencies.core import get_chat_pipeline_use_case, _chat_session_repo
from backend.core.domain.chat import ChatSession, ChatMessage, Citation

client = TestClient(app)

class MockChatPipelineUseCase:
    async def execute(self, query, session_id, collection_name):
        session = ChatSession(session_id="session_123")
        msg = ChatMessage(role="assistant", content="Response", citations=[
            Citation(document_id="doc1", document_type="resume", section_type="exp", chunk_index=0)
        ])
        return "Response", msg, session

    async def execute_stream(self, query, session_id, collection_name):
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
    with patch("backend.api.chat.EvaluationService") as mock_eval:
        response = client.post("/api/v1/chat", json={"query": "hello", "session_id": "session_123"})
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Response"
        assert data["session_id"] == "session_123"
        assert len(data["citations"]) == 1

def test_chat_endpoint_error(mock_use_case, monkeypatch):
    async def mock_execute(*args, **kwargs):
        raise Exception("Pipeline error")
    monkeypatch.setattr(mock_use_case, "execute", mock_execute)
    response = client.post("/api/v1/chat", json={"query": "hello"})
    assert response.status_code == 500

def test_chat_stream_endpoint(mock_use_case):
    response = client.post("/api/v1/chat/stream", json={"query": "hello"})
    assert response.status_code == 200
    # TestClient doesn't easily test SSE, but we can check if it returns 200

def test_chat_stream_error(mock_use_case, monkeypatch):
    def mock_execute_stream(*args, **kwargs):
        raise Exception("Stream error")
    monkeypatch.setattr(mock_use_case, "execute_stream", mock_execute_stream)
    response = client.post("/api/v1/chat/stream", json={"query": "hello"})
    assert response.status_code == 500

def test_get_history():
    session = ChatSession(session_id="session_456")
    _chat_session_repo.save(session)
    
    response = client.get("/api/v1/chat/session_456/history")
    assert response.status_code == 200
    assert response.json()["session_id"] == "session_456"
    
    response_missing = client.get("/api/v1/chat/missing/history")
    assert response_missing.status_code == 404

def test_delete_session():
    session = ChatSession(session_id="session_789")
    _chat_session_repo.save(session)
    
    response = client.delete("/api/v1/chat/session_789")
    assert response.status_code == 200
    
    response_missing = client.delete("/api/v1/chat/missing")
    assert response_missing.status_code == 404
