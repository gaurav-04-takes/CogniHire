from abc import ABC, abstractmethod
from typing import List

class IEmbedder(ABC):
    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of document chunks."""
        pass

    @abstractmethod
    def embed_query(self, query: str) -> List[float]:
        """Embed a search query."""
        pass
