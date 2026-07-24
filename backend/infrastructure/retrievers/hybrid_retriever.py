from typing import List, Dict, Any, Optional
from backend.core.interfaces.retriever import IRetriever
from backend.core.domain.chunk import Chunk

class HybridRetriever(IRetriever):
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
