"""
BM25 lexical retrieval implementation.

Architectural layer:
    Infrastructure.

Purpose:
    Implements IRetriever to perform exact keyword matching using the BM25 algorithm.
    Useful for exact matches on names, tools, or specific jargon where semantic
    search falls short.

Data flow:
    Pulls candidate chunks from the Index Repository based on metadata filters,
    tokenizes them, and calculates BM25 scores against the tokenized query.

Key dependencies:
    - rank_bm25
    - backend.core.interfaces.retriever

Related modules:
    - backend.infrastructure.vectorstores.chroma_repository
"""
from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Plus
from backend.core.interfaces.retriever import IRetriever
from backend.core.interfaces.index_repository import IIndexRepository
from backend.core.domain.chunk import Chunk

class BM25Retriever(IRetriever):
    """
    Lexical search retriever using BM25+.
    """
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
        
        Args:
            query: The raw search string.
            collection_name: Vector store collection to pull candidates from.
            filters: Pre-filtering criteria to reduce the BM25 search space.
            top_k: Max number of results.
            
        Returns:
            A list of Chunks sorted by BM25 score descending. Only chunks with 
            scores > 0 are returned.
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
