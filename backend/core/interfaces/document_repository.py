from abc import ABC, abstractmethod
from typing import List, Optional
from backend.core.domain.document import DocumentRecord

class IDocumentRepository(ABC):
    @abstractmethod
    def save(self, record: DocumentRecord) -> None:
        """Save or update a document record."""
        pass

    @abstractmethod
    def get(self, document_id: str) -> Optional[DocumentRecord]:
        """Retrieve a document record by ID."""
        pass

    @abstractmethod
    def get_all(self) -> List[DocumentRecord]:
        """Retrieve all document records."""
        pass

    @abstractmethod
    def delete(self, document_id: str) -> None:
        """Delete a document record."""
        pass
