from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Plus
from backend.core.interfaces.retriever import IRetriever
from backend.core.interfaces.index_repository import IIndexRepository
from backend.core.domain.chunk import Chunk

class BM25Retriever(IRetriever):
    def __init__(self, index_repository: IIndexRepository):
        self.index_repository = index_repository

    def retrieve(
        self, 
        query: str, 
        collection_name: str, 
        filters: Optional[Dict[str, Any]] = None, 
        top_k: int = 5
    ) -> List[Chunk]:
        """
        Retrieves relevant chunks using BM25 exact keyword matching.
        """
        # Fetch candidate chunks from repository matching filters
        chunks = self.index_repository.get_chunks(collection_name=collection_name, filters=filters)
        
        if not chunks:
            return []
            
        # Tokenize chunks for BM25 (simple whitespace tokenization for prototype)
        tokenized_corpus = [chunk.text.lower().split() for chunk in chunks]
        
        bm25 = BM25Plus(tokenized_corpus)
        
        tokenized_query = query.lower().split()
        scores = bm25.get_scores(tokenized_query)
        
        # Attach scores and sort
        query_set = set(tokenized_query)
        for i, chunk in enumerate(chunks):
            chunk_tokens = set(chunk.text.lower().split())
            if any(q in chunk_tokens for q in query_set):
                chunk.score = scores[i]
            else:
                chunk.score = 0.0
            
        # Sort by score descending
        chunks.sort(key=lambda x: x.score or 0.0, reverse=True)
        
        # Return top_k chunks that have a positive score
        return [c for c in chunks if (c.score is not None and c.score > 0)][:top_k]
