import chromadb
from typing import List, Dict, Any, Optional
from backend.core.interfaces.index_repository import IIndexRepository
from backend.core.domain.chunk import Chunk
from backend.core.domain.document import DocumentType

class ChromaIndexRepository(IIndexRepository):
    def __init__(self, persist_directory: str, embedder):
        # embedder should implement an interface compatible with Chroma's EmbeddingFunction
        # or we manually embed before inserting. We will manually embed in the pipeline.
        self.client = chromadb.PersistentClient(path=persist_directory)
        
    def index_chunks(self, chunks: List[Chunk], collection_name: str) -> None:
        if not chunks:
            return
            
        collection = self.client.get_or_create_collection(name=collection_name)
        
        ids = [chunk.id for chunk in chunks]
        texts = [chunk.text for chunk in chunks]
        # Ensure metadata values are str, int, float or bool (Chroma restriction)
        metadatas = []
        for chunk in chunks:
            meta = chunk.metadata.copy()
            # Clean metadata for chromadb
            cleaned_meta = {k: v for k, v in meta.items() if isinstance(v, (str, int, float, bool))}
            metadatas.append(cleaned_meta)
            
        # We assume embeddings are generated beforehand, or we pass them in if we update the interface
        # Wait, the interface IIndexRepository.index_chunks doesn't take embeddings, 
        # so the pipeline must either attach embeddings to the Chunk object, or Chroma computes them.
        # Given we have BGEEmbeddingProvider, we should attach them to Chunk or pass them here.
        # Let's assume chunks have a hidden or extra field, or we update Chunk domain to hold embedding.
        
        # Wait, we need the embeddings! Let's update Chunk domain to optionally hold embedding.
        # For now, let's just insert texts and let Chroma handle it if no embedding is provided,
        # but we WANT to use our BGEProvider. 
        # I'll modify the interface to accept embeddings, or assume chunk.metadata["embedding"] exists.
        
        embeddings = [chunk.metadata.pop("embedding") for chunk in chunks if "embedding" in chunk.metadata]
        
        if len(embeddings) == len(chunks):
            collection.add(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)
        else:
            collection.add(ids=ids, documents=texts, metadatas=metadatas)

    def delete_document(self, document_id: str, collection_name: str) -> None:
        try:
            collection = self.client.get_collection(name=collection_name)
            collection.delete(where={"document_id": document_id})
        except Exception:
            pass # Collection doesn't exist

    def search(self, query_embedding: List[float], collection_name: str, filters: Optional[Dict[str, Any]] = None, top_k: int = 5) -> List[Chunk]:
        try:
            collection = self.client.get_collection(name=collection_name)
        except Exception:
            return []
            
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filters
        )
        
        chunks = []
        if results['ids'] and len(results['ids']) > 0:
            for i in range(len(results['ids'][0])):
                chunk = Chunk(
                    id=results['ids'][0][i],
                    document_id=results['metadatas'][0][i].get("document_id", ""),
                    doc_type=DocumentType(results['metadatas'][0][i].get("document_type", "unknown")),
                    section_type=results['metadatas'][0][i].get("section_type"),
                    text=results['documents'][0][i],
                    metadata=results['metadatas'][0][i],
                    score=results['distances'][0][i] if 'distances' in results and results['distances'] else None
                )
                chunks.append(chunk)
                
        return chunks

    def get_chunks(self, collection_name: str, filters: Optional[Dict[str, Any]] = None) -> List[Chunk]:
        try:
            collection = self.client.get_collection(name=collection_name)
        except Exception:
            return []
            
        results = collection.get(where=filters)
        
        chunks = []
        if results['ids'] and len(results['ids']) > 0:
            for i in range(len(results['ids'])):
                chunk = Chunk(
                    id=results['ids'][i],
                    document_id=results['metadatas'][i].get("document_id", ""),
                    doc_type=DocumentType(results['metadatas'][i].get("document_type", "unknown")),
                    section_type=results['metadatas'][i].get("section_type"),
                    text=results['documents'][i],
                    metadata=results['metadatas'][i]
                )
                chunks.append(chunk)
                
        return chunks
