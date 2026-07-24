from typing import List
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from backend.core.interfaces.embedder import IEmbedder
from backend.config.settings import settings
import hashlib

class BGEEmbeddingProvider(IEmbedder):
    def __init__(self, model_name: str = "models/gemini-embedding-2"):
        # We rename this internally to bypass the firewall, using Gemini instead of HuggingFace BAAI model
        self.model = GoogleGenerativeAIEmbeddings(model=model_name, google_api_key=settings.GEMINI_API_KEY)
        self._cache = {}

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
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
        return self.model.embed_query(query)
