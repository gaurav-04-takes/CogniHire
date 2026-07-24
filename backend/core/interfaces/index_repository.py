from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..domain.chunk import Chunk

class IIndexRepository(ABC):
    @abstractmethod
    def index_chunks(self, chunks: List[Chunk], collection_name: str) -> None:
        """Store chunks and their embeddings in the vector database."""
        pass

    @abstractmethod
    def delete_document(self, document_id: str, collection_name: str) -> None:
        """Remove all chunks associated with a specific document."""
        pass
        
    @abstractmethod
    def search(self, query_embedding: List[float], collection_name: str, filters: Optional[Dict[str, Any]] = None, top_k: int = 5) -> List[Chunk]:
        """Search the index for relevant chunks."""
        pass

    @abstractmethod
    def get_chunks(self, collection_name: str, filters: Optional[Dict[str, Any]] = None) -> List[Chunk]:
        """Retrieve chunks from the index, optionally matching filters. Useful for BM25 model building."""
        pass
