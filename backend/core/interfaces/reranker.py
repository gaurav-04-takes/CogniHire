"""
Document reranking interface.

Architectural layer:
    Core interfaces.

Purpose:
    Defines the contract for scoring and re-ordering chunks based on query relevance.

Data flow:
    Receives candidate chunks from retrievers and a query, returning a sorted
    subset of those chunks.

Key dependencies:
    - Chunk domain object.

Related modules:
    - backend.infrastructure.rerankers.bge_reranker
"""
from abc import ABC, abstractmethod
from typing import List
from ..domain.chunk import Chunk

class IReranker(ABC):
    """
    Defines the abstraction for a cross-encoder or reranking model.

    Used by the application to refine the order of chunks returned by
    initial retrieval methods, improving overall RAG accuracy.
    """
    @abstractmethod
    def rerank(self, query: str, chunks: List[Chunk], top_k: int = 5) -> List[Chunk]:
        """
        Rerank a list of retrieved chunks based on their relevance to the query.

        Args:
            query: The user query string.
            chunks: The initial list of Chunk candidates.
            top_k: The maximum number of top-scoring chunks to return.

        Returns:
            A new list of Chunks, sorted descending by their reranked scores.
        """
        pass
