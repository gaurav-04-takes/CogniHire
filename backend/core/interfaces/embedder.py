"""
Text embedding interface.

Architectural layer:
    Core interfaces.

Purpose:
    Defines the contract for converting text into dense vector embeddings.

Data flow:
    Implementations receive text strings from the indexing or retrieval
    pipelines and return lists of floats representing vectors.

Key dependencies:
    None.

Related modules:
    - backend.infrastructure.embedders.bge_embedder
"""
from abc import ABC, abstractmethod
from typing import List

class IEmbedder(ABC):
    """
    Defines the abstraction for an embedding model.

    Application services and retrievers depend on this interface so they
    are decoupled from specific models like Sentence Transformers or OpenAI.
    """
    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of document chunks.

        Args:
            texts: A list of text chunks to be embedded during ingestion.

        Returns:
            A list of dense vectors corresponding to the input texts.
        """
        pass

    @abstractmethod
    def embed_query(self, query: str) -> List[float]:
        """
        Embed a search query.

        Args:
            query: A single query string (e.g., from a user or analysis service).

        Returns:
            A dense vector representation of the query.
        """
        pass
