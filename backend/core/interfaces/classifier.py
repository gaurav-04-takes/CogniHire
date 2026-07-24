from abc import ABC, abstractmethod
from ..domain.document import DocumentType, ClassificationResult

class IDocumentClassifier(ABC):
    @abstractmethod
    def classify(self, text: str) -> ClassificationResult:
        """Classify a document's text as either Resume or Job Description."""
        pass
