"""
Simple Hybrid Retriever implementation.

Architectural layer:
    Infrastructure.

Purpose:
    Combines results from a Vector Retriever and a BM25 Retriever by simply
    interleaving their outputs. 

Data flow:
    Calls two child retrievers independently, merges their outputs sequentially,
    deduplicates by chunk ID, and returns the combined list.

Key dependencies:
    - backend.core.interfaces.retriever

Related modules:
    - backend.infrastructure.retrievers.rrf_retriever (alternative merger)
"""
from typing import List, Dict, Any, Optional
from backend.core.interfaces.retriever import IRetriever
from backend.core.domain.chunk import Chunk

class HybridRetriever(IRetriever):
    """
    Interleaving hybrid retriever.
    
    A simpler alternative to RRF. Takes the top result from Vector, then the top
    from BM25, then the second from Vector, etc.
    """
    def __init__(self, vector_retriever: IRetriever, bm25_retriever: IRetriever):
        self.vector_retriever = vector_retriever
        self.bm25_retriever = bm25_retriever

    def retrieve(
        self, 
        query: str, 
        collection_name: str, 
        filters: Optional[Dict[str, Any]] = None, 
        top_k: int = 5
    ) -> List[Chunk]:
        """
        Retrieves relevant chunks by combining Vector and BM25 search.
        
        Args:
            query: The search string.
            collection_name: Target vector collection.
            filters: Metadata filters passed to both retrievers.
            top_k: Max total results returned after merging.
            
        Returns:
            A deduplicated, interleaved list of Chunk objects.
        """
        vector_results = self.vector_retriever.retrieve(query, collection_name, filters, top_k)
        bm25_results = self.bm25_retriever.retrieve(query, collection_name, filters, top_k)
        
        # Merge logic: Interleave results, preserving order, avoiding duplicates
        merged = []
        seen_ids = set()
        
        # Interleave
        max_len = max(len(vector_results), len(bm25_results))
        for i in range(max_len):
            if i < len(vector_results):
                v_chunk = vector_results[i]
                if v_chunk.id not in seen_ids:
                    merged.append(v_chunk)
                    seen_ids.add(v_chunk.id)
                    
            if i < len(bm25_results):
                b_chunk = bm25_results[i]
                if b_chunk.id not in seen_ids:
                    merged.append(b_chunk)
                    seen_ids.add(b_chunk.id)
                    
        return merged[:top_k]
