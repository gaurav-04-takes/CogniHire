from abc import ABC, abstractmethod
from typing import List
from ..domain.chunk import Chunk

class IReranker(ABC):
    @abstractmethod
    def rerank(self, query: str, chunks: List[Chunk], top_k: int = 5) -> List[Chunk]:
        """Rerank a list of retrieved chunks based on their relevance to the query."""
        pass
