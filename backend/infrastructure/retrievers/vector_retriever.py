from typing import List, Dict, Any, Optional
from backend.core.interfaces.retriever import IRetriever
from backend.core.interfaces.embedder import IEmbedder
from backend.core.interfaces.index_repository import IIndexRepository
from backend.core.domain.chunk import Chunk

class VectorRetriever(IRetriever):
    def __init__(self, embedder: IEmbedder, index_repository: IIndexRepository):
        self.embedder = embedder
        self.index_repository = index_repository

    def retrieve(
        self, 
        query: str, 
        collection_name: str, 
        filters: Optional[Dict[str, Any]] = None, 
        top_k: int = 5
    ) -> List[Chunk]:
        """
        Retrieves relevant chunks by embedding the query and searching ChromaDB.
        """
        # 1. Generate query embedding
        query_embedding = self.embedder.embed_query(query)
        
        # 2. Search ChromaDB
        chunks = self.index_repository.search(
            query_embedding=query_embedding,
            collection_name=collection_name,
            filters=filters,
            top_k=top_k
        )
        
        return chunks
