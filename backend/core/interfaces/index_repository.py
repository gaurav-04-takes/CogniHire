"""
Vector index repository interface.

Architectural layer:
    Core interfaces.

Purpose:
    Defines the contract for storing and querying vector embeddings and chunk metadata.

Data flow:
    Receives Chunk objects from the indexing pipeline and stores them.
    Receives query vectors and returns matching Chunk objects during retrieval.

Key dependencies:
    - Chunk domain object.

Related modules:
    - backend.infrastructure.vectorstores.chroma_repository
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..domain.chunk import Chunk

class IIndexRepository(ABC):
    """
    Defines the abstraction for the vector database.

    Application services and retrievers interact with this interface rather
    than directly calling ChromaDB or another vector store. This ensures
    domain objects (Chunks) are used instead of store-specific dictionaries.
    """
    @abstractmethod
    def index_chunks(self, chunks: List[Chunk], collection_name: str) -> None:
        """
        Store chunks and their embeddings in the vector database.

        Args:
            chunks: List of Chunk objects containing text, embeddings, and metadata.
            collection_name: The name of the logical collection to store chunks in.

        Side Effects:
            Writes data to the underlying vector database.
        """
        pass

    @abstractmethod
    def delete_document(self, document_id: str, collection_name: str) -> None:
        """
        Remove all chunks associated with a specific document.

        Args:
            document_id: The ID of the document whose chunks should be deleted.
            collection_name: The collection containing the document's chunks.

        Side Effects:
            Removes associated vectors and metadata from the vector database.
        """
        pass
        
    @abstractmethod
    def search(self, query_embedding: List[float], collection_name: str, filters: Optional[Dict[str, Any]] = None, top_k: int = 5) -> List[Chunk]:
        """
        Search the index for relevant chunks.

        Args:
            query_embedding: The dense vector representation of the search query.
            collection_name: The collection to search within.
            filters: Metadata restrictions (e.g., document_id, document_type).
            top_k: Maximum number of chunks to return.

        Returns:
            A list of Chunk objects ordered by vector similarity.
        """
        pass

    @abstractmethod
    def get_chunks(self, collection_name: str, filters: Optional[Dict[str, Any]] = None) -> List[Chunk]:
        """
        Retrieve chunks from the index, optionally matching filters. 

        Useful for BM25 model building or exact keyword retrieval over a subset
        of indexed documents.

        Args:
            collection_name: The collection to retrieve chunks from.
            filters: Optional metadata restrictions.

        Returns:
            A list of all matching Chunk objects.
        """
        pass
