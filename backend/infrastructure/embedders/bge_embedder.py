"""
Embedding generation using Google Gemini.

Architectural layer:
    Infrastructure.

Purpose:
    Implements the IEmbedder interface to convert text chunks and queries 
    into dense vector embeddings. Provides an in-memory caching layer to
    prevent redundant API calls for duplicate texts.

Data flow:
    Receives strings from the indexing or retrieval pipeline, requests 
    embeddings from Google Generative AI, and returns float vectors.

Key dependencies:
    - langchain_google_genai
    - backend.core.interfaces.embedder

Side effects:
    - Makes external network requests to Google Gemini API.
    - Modifies in-memory `_cache` dictionary.

Related modules:
    - backend.application.use_cases.ingest_document
"""
from typing import List
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from backend.core.interfaces.embedder import IEmbedder
from backend.config.settings import settings
import hashlib

class BGEEmbeddingProvider(IEmbedder):
    """
    Embedding provider utilizing Google Generative AI.
    
    Originally intended for BAAI/bge-large-en-v1.5, this has been aliased
    to Gemini to comply with corporate firewall restrictions against HuggingFace.
    """
    def __init__(self, model_name: str = "models/gemini-embedding-2"):
        # We rename this internally to bypass the firewall, using Gemini instead of HuggingFace BAAI model
        self.model = GoogleGenerativeAIEmbeddings(model=model_name, google_api_key=settings.GEMINI_API_KEY)
        self._cache = {}

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embeds a list of document chunks, utilizing an in-memory cache.
        
        Hashes each string to check the cache before calling the external API.
        Only un-cached strings are sent over the network.
        
        Args:
            texts: List of strings (e.g., chunk content) to embed.
            
        Returns:
            A list of embedding vectors corresponding 1:1 with the input texts.
        """
        embeddings = []
        uncached_texts = []
        uncached_indices = []
        
        for i, text in enumerate(texts):
            text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
            if text_hash in self._cache:
                embeddings.append(self._cache[text_hash])
            else:
                embeddings.append(None)
                uncached_texts.append(text)
                uncached_indices.append(i)
                
        if uncached_texts:
            new_embeddings = self.model.embed_documents(uncached_texts)
            for idx, text, emb in zip(uncached_indices, uncached_texts, new_embeddings):
                text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
                self._cache[text_hash] = emb
                embeddings[idx] = emb
                
        return embeddings

    def embed_query(self, query: str) -> List[float]:
        """
        Embeds a single search query.
        
        Queries are typically not cached here to allow dynamic context, though
        application-level caching may apply elsewhere.
        
        Args:
            query: The user's input text.
            
        Returns:
            A single dense float vector.
        """
        return self.model.embed_query(query)
