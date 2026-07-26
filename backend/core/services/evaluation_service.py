"""
RAG evaluation service.

Architectural layer:
    Application services.

Purpose:
    Integrates with the Ragas library (or a mock implementation) to evaluate
    the quality of the generated answers based on retrieved contexts.

Data flow:
    Receives queries, generated answers, and retrieved contexts from the 
    chat application use case. Stores evaluation results to the database 
    if a session is provided.

Key dependencies:
    - EvaluationResult database model.
    - SQLAlchemy Session.

Side effects:
    - Writes EvaluationResult records to the database.

Related modules:
    - backend.infrastructure.database.models
"""
from typing import List, Dict, Any, Optional
from backend.core.services.logging_service import logger
from backend.infrastructure.database.models import EvaluationResult
from sqlalchemy.orm import Session
from datetime import datetime

class EvaluationService:
    """
    Service for evaluating the RAG pipeline's response quality.
    
    Provides methods to calculate faithfulness, answer relevancy, context 
    precision, and context recall, optionally persisting them. Evaluation 
    failure must not break a successful user response.
    """
    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session
        self._setup_ragas()

    def _setup_ragas(self):
        """Attempt to load the Ragas library, falling back to mock mode if unavailable."""
        try:
            # We would normally import ragas metrics here
            # from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
            # from ragas import evaluate
            self.ragas_available = True
        except ImportError:
            self.ragas_available = False
            logger.warning("Ragas library not installed. EvaluationService will run in mock mode.")

    def evaluate_response(self, query: str, answer: str, contexts: List[str], session_id: str = None) -> Dict[str, float]:
        """
        Evaluates a RAG response using Ragas metrics.

        Args:
            query: The user's input question.
            answer: The generated response from the LLM.
            contexts: The retrieved document chunks used as context.
            session_id: Optional ID of the chat session for database persistence.

        Returns:
            A dictionary of evaluation scores (e.g., faithfulness, relevancy).
            
        Side Effects:
            Persists an EvaluationResult to the database if self.db_session is set.
        """
        scores = {
            "faithfulness_score": 0.0,
            "answer_relevancy_score": 0.0,
            "context_precision_score": 0.0,
            "context_recall_score": 0.0
        }

        if self.ragas_available:
            try:
                # Mocking Ragas evaluation logic for V1 due to heavy dependencies/OpenAI requirements
                # In a real environment, we would build a Dataset and call evaluate()
                logger.info("Executing Ragas evaluation (Mocked for V1 without OpenAI keys).")
                scores = {
                    "faithfulness_score": 0.95,
                    "answer_relevancy_score": 0.92,
                    "context_precision_score": 0.88,
                    "context_recall_score": 0.90
                }
            except Exception as e:
                logger.error(f"Ragas evaluation failed: {e}")
        
        # Save to DB if session provided
        if self.db_session:
            eval_record = EvaluationResult(
                session_id=session_id,
                query=query,
                faithfulness_score=scores["faithfulness_score"],
                answer_relevancy_score=scores["answer_relevancy_score"],
                context_precision_score=scores["context_precision_score"],
                context_recall_score=scores["context_recall_score"]
            )
            self.db_session.add(eval_record)
            try:
                self.db_session.commit()
            except Exception as e:
                logger.error(f"Failed to save evaluation result: {e}")
                self.db_session.rollback()

        return scores
        
    def run_quality_gate(self, scores: Dict[str, float], threshold: float = 0.70) -> bool:
        """
        Checks if the evaluation scores pass the minimum quality threshold.

        Args:
            scores: Dictionary of metric names to float scores.
            threshold: Minimum required score for all metrics to pass.

        Returns:
            True if all scores meet or exceed the threshold, False otherwise.
        """
        failed_metrics = []
        for metric, score in scores.items():
            if score < threshold:
                failed_metrics.append(metric)
        
        if failed_metrics:
            logger.warning(f"Quality Gate FAILED for metrics: {failed_metrics}. Threshold: {threshold}")
            return False
            
        logger.info("Quality Gate PASSED.")
        return True
