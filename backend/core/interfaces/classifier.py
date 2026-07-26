"""
Document classification interface.

Architectural layer:
    Core interfaces.

Purpose:
    Defines the contract for classifying a document's raw text as either
    a Resume or Job Description.

Data flow:
    Implementations receive raw text from the ingestion pipeline and return
    a ClassificationResult DTO.

Key dependencies:
    - ClassificationResult domain object.

Related modules:
    - backend.infrastructure.classifiers.rule_based_classifier
"""
from abc import ABC, abstractmethod
from ..domain.document import DocumentType, ClassificationResult

class IDocumentClassifier(ABC):
    """
    Defines the abstraction for document classification.

    Application services depend on this interface instead of a specific
    classification implementation (e.g., rule-based or machine learning).
    """
    @abstractmethod
    def classify(self, text: str) -> ClassificationResult:
        """
        Classify a document's text as either Resume or Job Description.

        Args:
            text: The normalized raw text extracted from the document.

        Returns:
            A ClassificationResult object containing the determined DocumentType
            and the confidence score.
        """
        pass
