from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..domain.chunk import Chunk

class IRetriever(ABC):
    @abstractmethod
    def retrieve(self, query: str, collection_name: str, filters: Optional[Dict[str, Any]] = None, top_k: int = 5) -> List[Chunk]:
        """Retrieve the most relevant chunks for a given query."""
        pass
