import pytest
from backend.core.services.evaluation_service import EvaluationService

def test_evaluation_service_mock():
    # Setup
    eval_service = EvaluationService()
    
    # Act
    scores = eval_service.evaluate_response("What is Python?", "Python is a language", ["Context 1"])
    
    # Assert
    assert "faithfulness_score" in scores
    assert "answer_relevancy_score" in scores
    assert "context_precision_score" in scores
    assert "context_recall_score" in scores
    
def test_quality_gate_pass():
    eval_service = EvaluationService()
    scores = {
        "faithfulness_score": 0.8,
        "answer_relevancy_score": 0.8
    }
    assert eval_service.run_quality_gate(scores, threshold=0.7) is True

def test_quality_gate_fail():
    eval_service = EvaluationService()
    scores = {
        "faithfulness_score": 0.6,
        "answer_relevancy_score": 0.8
    }
    assert eval_service.run_quality_gate(scores, threshold=0.7) is False
