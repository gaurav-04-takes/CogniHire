import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from backend.main import app
from backend.infrastructure.database.session import SessionLocal
from backend.infrastructure.database.models import FeedbackRecord, Base
from backend.infrastructure.database.session import SessionLocal, engine
from backend.dependencies.core import get_index_repository, get_chat_pipeline_use_case

client = TestClient(app)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # cleanup feedback table
        db.query(FeedbackRecord).delete()
        db.commit()
        yield db
    finally:
        db.close()

def test_health_database():
    response = client.get("/api/v1/health/database")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_health_disk():
    response = client.get("/api/v1/health/disk")
    assert response.status_code == 200
    assert response.json()["status"] in ["ok", "warning"]

def test_health_evaluation():
    response = client.get("/api/v1/health/evaluation")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_feedback_submit_valid(db_session):
    data = {
        "score": 5,
        "comment": "Great!",
        "session_id": "sess-1",
        "response_id": "resp-1",
        "query": "hi"
    }
    response = client.post("/api/v1/feedback", json=data)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    
    # Verify in DB
    record = db_session.query(FeedbackRecord).filter_by(session_id="sess-1").first()
    assert record is not None
    assert record.score == 5
    assert record.comment == "Great!"

def test_feedback_submit_invalid_score(db_session):
    data = {"score": 6}
    response = client.post("/api/v1/feedback", json=data)
    assert response.status_code == 400

def test_feedback_get(db_session):
    # submit one
    data = {"score": 4, "comment": "Good"}
    client.post("/api/v1/feedback", json=data)
    
    response = client.get("/api/v1/feedback")
    assert response.status_code == 200
    res_list = response.json()
    assert len(res_list) >= 1
    assert res_list[0]["score"] == 4
    assert res_list[0]["comment"] == "Good"
