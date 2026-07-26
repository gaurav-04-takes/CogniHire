"""
Document retrieval interface.

Architectural layer:
    Core interfaces.

Purpose:
    Defines the contract for retrieving relevant chunks from the index.

Data flow:
    Receives queries and metadata filters from application use cases,
    and returns relevant Chunk entities from the vector store or search index.

Key dependencies:
    - Chunk domain object.

Related modules:
    - backend.infrastructure.retrievers.vector_retriever
    - backend.infrastructure.retrievers.bm25_retriever
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..domain.chunk import Chunk

class IRetriever(ABC):
    """
    Defines the abstraction for document retrieval strategies.

    Allows the application to swap or combine different retrieval methods
    (e.g., semantic search, BM25, hybrid) without altering core logic.
    """
    @abstractmethod
    def retrieve(self, query: str, collection_name: str, filters: Optional[Dict[str, Any]] = None, top_k: int = 5) -> List[Chunk]:
        """
        Retrieve the most relevant chunks for a given query.

        Args:
            query: The search query string.
            collection_name: The index collection to search within.
            filters: Optional metadata restrictions (e.g., document ID limits).
            top_k: The maximum number of candidate chunks to return.

        Returns:
            A list of Chunk objects ordered by their retrieval score.
        """
        pass
