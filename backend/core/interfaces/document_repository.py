"""
Document persistence interface.

Architectural layer:
    Core interfaces.

Purpose:
    Defines the contract for saving and retrieving DocumentRecord entities.

Data flow:
    Use cases pass domain models to implementations of this interface,
    which handle the translation to database-specific representations.

Key dependencies:
    - DocumentRecord domain object.

Related modules:
    - backend.infrastructure.repositories.sqlite_document_repository
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from backend.core.domain.document import DocumentRecord

class IDocumentRepository(ABC):
    """
    Defines the abstraction for relational document persistence.

    Application services use this interface to track uploaded documents,
    their processing status, and their classification. Implementations
    must translate between the domain DocumentRecord and the underlying
    database models.
    """
    @abstractmethod
    def save(self, record: DocumentRecord) -> None:
        """
        Save or update a document record.

        Args:
            record: The domain DocumentRecord to persist.

        Side Effects:
            Writes or updates a record in the underlying relational database.
        """
        pass

    @abstractmethod
    def get(self, document_id: str) -> Optional[DocumentRecord]:
        """
        Retrieve a document record by ID.

        Args:
            document_id: The unique identifier of the document.

        Returns:
            The DocumentRecord if found, otherwise None.
        """
        pass

    @abstractmethod
    def get_all(self) -> List[DocumentRecord]:
        """
        Retrieve all document records.

        Returns:
            A list of all DocumentRecord entities currently stored.
        """
        pass

    @abstractmethod
    def delete(self, document_id: str) -> None:
        """
        Delete a document record.

        Args:
            document_id: The unique identifier of the document to remove.

        Side Effects:
            Removes the record from the underlying relational database.
        """
        pass
