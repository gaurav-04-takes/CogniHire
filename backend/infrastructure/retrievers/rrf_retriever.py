"""
Reciprocal Rank Fusion (RRF) Retriever implementation.

Architectural layer:
    Infrastructure.

Purpose:
    Combines dense and lexical search results mathematically using the RRF
    algorithm. RRF assigns a score based on the rank of a document in each
    sub-retriever's result set, mitigating scale differences between distance
    metrics (e.g., Cosine vs BM25).

Data flow:
    Over-fetches from child retrievers, calculates RRF scores for all unique
    documents, and returns the top_k by fused score.

Key dependencies:
    - backend.core.interfaces.retriever

Related modules:
    None.
"""
from typing import List, Dict, Any, Optional
from backend.core.interfaces.retriever import IRetriever
from backend.core.domain.chunk import Chunk

class RRFRetriever(IRetriever):
    """
    Advanced hybrid retriever utilizing Reciprocal Rank Fusion.
    """
    def __init__(self, vector_retriever: IRetriever, bm25_retriever: IRetriever, k: int = 60):
        self.vector_retriever = vector_retriever
        self.bm25_retriever = bm25_retriever
        self.k = k

    def retrieve(
        self, 
        query: str, 
        collection_name: str, 
        filters: Optional[Dict[str, Any]] = None, 
        top_k: int = 5
    ) -> List[Chunk]:
        """
        Retrieves chunks using both vector and BM25 retrievers,
        and fuses their rankings using Reciprocal Rank Fusion (RRF).
        
        Args:
            query: The search string.
            collection_name: The vector collection to query.
            filters: Metadata filters applied to sub-retrievers.
            top_k: Number of fused results to return.
            
        Returns:
            A list of Chunks, with the `score` field overwritten by the
            calculated RRF score.
        """
        # Fetch results from both retrievers (fetching more to fuse effectively)
        fetch_k = max(top_k * 2, 20)
        vector_results = self.vector_retriever.retrieve(query, collection_name, filters, top_k=fetch_k)
        bm25_results = self.bm25_retriever.retrieve(query, collection_name, filters, top_k=fetch_k)
        
        rrf_scores: Dict[str, float] = {}
        all_chunks: Dict[str, Chunk] = {}
        
        # Calculate RRF score for vector results
        for rank, chunk in enumerate(vector_results):
            # 1-indexed rank
            score = 1.0 / (self.k + rank + 1)
            rrf_scores[chunk.id] = rrf_scores.get(chunk.id, 0.0) + score
            all_chunks[chunk.id] = chunk
            
        # Calculate RRF score for BM25 results
        for rank, chunk in enumerate(bm25_results):
            score = 1.0 / (self.k + rank + 1)
            rrf_scores[chunk.id] = rrf_scores.get(chunk.id, 0.0) + score
            all_chunks[chunk.id] = chunk
            
        # Update chunk scores and sort
        for chunk_id, score in rrf_scores.items():
            all_chunks[chunk_id].score = score
            
        ranked_chunks = sorted(all_chunks.values(), key=lambda x: x.score or 0.0, reverse=True)
        return ranked_chunks[:top_k]
