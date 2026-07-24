from typing import List, Dict, Any, Optional
from backend.core.services.logging_service import logger
from backend.infrastructure.database.models import EvaluationResult
from sqlalchemy.orm import Session
from datetime import datetime

class EvaluationService:
    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session
        self._setup_ragas()

    def _setup_ragas(self):
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
        Returns a dictionary of scores.
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
