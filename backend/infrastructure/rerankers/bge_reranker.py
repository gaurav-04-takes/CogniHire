from typing import List
from backend.core.interfaces.reranker import IReranker
from backend.core.domain.chunk import Chunk

class BGEReranker(IReranker):
    def __init__(self, model_name: str = "dummy"):
        pass

    def rerank(self, query: str, chunks: List[Chunk], top_k: int = 5) -> List[Chunk]:
        """
        Pass-through reranker that bypasses HuggingFace cross-encoder for firewall compatibility.
        """
        if not chunks:
            return []
        
        # Simply return the top chunks from the initial retrieval
        return chunks[:top_k]
