"""
Dense Vector Retriever implementation.

Architectural layer:
    Infrastructure.

Purpose:
    Retrieves documents by converting the user query into a dense embedding
    and performing a similarity search against the vector database.
    Captures semantic meaning beyond exact keywords.

Data flow:
    Passes the query string to the Embedder, then passes the resulting vector
    and metadata filters to the IndexRepository.

Key dependencies:
    - backend.core.interfaces.embedder
    - backend.core.interfaces.index_repository

Related modules:
    - backend.infrastructure.vectorstores.chroma_repository
"""
from typing import List, Dict, Any, Optional
from backend.core.interfaces.retriever import IRetriever
from backend.core.interfaces.embedder import IEmbedder
from backend.core.interfaces.index_repository import IIndexRepository
from backend.core.domain.chunk import Chunk

class VectorRetriever(IRetriever):
    """
    Standard dense embedding retriever.
    """
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
        
        Args:
            query: The natural language search query.
            collection_name: The target vector collection.
            filters: Pre-filtering criteria to narrow the search space.
            top_k: Max number of vectors to return.
            
        Returns:
            A list of Chunks representing the nearest neighbors in vector space.
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
