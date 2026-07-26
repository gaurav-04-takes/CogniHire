"""
Cross-encoder reranking placeholder.

Architectural layer:
    Infrastructure.

Purpose:
    Intended to perform secondary cross-encoder reranking on retrieved chunks
    to improve precision. Currently acts as a pass-through due to firewall
    restrictions on HuggingFace model weights.

Data flow:
    Accepts a query and a list of Chunks, and returns them unchanged (truncated 
    to top_k).

Key dependencies:
    - backend.core.interfaces.reranker

Related modules:
    - backend.application.use_cases.chat
"""
from typing import List
from backend.core.interfaces.reranker import IReranker
from backend.core.domain.chunk import Chunk

class BGEReranker(IReranker):
    """
    Pass-through implementation of IReranker.
    """
    def __init__(self, model_name: str = "dummy"):
        pass

    def rerank(self, query: str, chunks: List[Chunk], top_k: int = 5) -> List[Chunk]:
        """
        Pass-through reranker that bypasses HuggingFace cross-encoder for firewall compatibility.
        
        Args:
            query: The search query (unused).
            chunks: The retrieved candidate chunks.
            top_k: Max results to return.
            
        Returns:
            The input chunks list truncated to top_k elements, maintaining their
            original order.
        """
        if not chunks:
            return []
        
        # Simply return the top chunks from the initial retrieval
        return chunks[:top_k]
