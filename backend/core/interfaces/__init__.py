"""
Core interfaces module.

Architectural layer:
    Core interfaces.

Purpose:
    Exports all core interfaces to simplify imports across the application.
    These abstractions define the contracts that the infrastructure layer
    must implement and that the application layer depends upon, enforcing
    the Dependency Inversion Principle.
"""
from .embedder import IEmbedder
from .retriever import IRetriever
from .reranker import IReranker
from .llm_provider import ILLMProvider
from .parser import IDocumentParser
from .classifier import IDocumentClassifier
from .section_parser import ISectionParser
from .index_repository import IIndexRepository

__all__ = [
    "IEmbedder",
    "IRetriever",
    "IReranker",
    "ILLMProvider",
    "IDocumentParser",
    "IDocumentClassifier",
    "ISectionParser",
    "IIndexRepository"
]
