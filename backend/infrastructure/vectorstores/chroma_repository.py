"""
ChromaDB vector store implementation.

Architectural layer:
    Infrastructure (Database access).

Purpose:
    Implements IIndexRepository to persist and query document chunks and their 
    embeddings using ChromaDB as the underlying vector database.

Data flow:
    Accepts domain Chunk objects, strips complex objects to conform to Chroma's
    metadata limitations, and writes to local disk. Returns Chunk objects on read.

Key dependencies:
    - chromadb
    - backend.core.interfaces.index_repository

Side effects:
    - Writes to the local filesystem (persist_directory).

Related modules:
    - backend.infrastructure.embedders.bge_embedder
"""
import chromadb
from typing import List, Dict, Any, Optional
from backend.core.interfaces.index_repository import IIndexRepository
from backend.core.domain.chunk import Chunk
from backend.core.domain.document import DocumentType

class ChromaIndexRepository(IIndexRepository):
    """
    Persistent ChromaDB index repository.
    
    Manages collection creation, document insertion (with embeddings),
    deletion, and both dense and metadata-only querying.
    """
    def __init__(self, persist_directory: str, embedder):
        # embedder should implement an interface compatible with Chroma's EmbeddingFunction
        # or we manually embed before inserting. We will manually embed in the pipeline.
        self.client = chromadb.PersistentClient(path=persist_directory)
        
    def index_chunks(self, chunks: List[Chunk], collection_name: str) -> None:
        """
        Inserts document chunks into a named Chroma collection.
        
        Extracts pre-computed embeddings from the chunk metadata. Removes 
        complex metadata types (dicts, lists) to comply with Chroma's storage limits.
        
        Args:
            chunks: List of populated Chunk domain objects.
            collection_name: Target Chroma collection name.
            
        Side Effects:
            Mutates state on disk in the Chroma persist directory.
        """
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
        """
        Deletes all chunks belonging to a specific document ID.
        
        Args:
            document_id: The UUID of the document to purge.
            collection_name: The target collection.
        """
        try:
            collection = self.client.get_collection(name=collection_name)
            collection.delete(where={"document_id": document_id})
        except Exception:
            pass # Collection doesn't exist

    def search(self, query_embedding: List[float], collection_name: str, filters: Optional[Dict[str, Any]] = None, top_k: int = 5) -> List[Chunk]:
        """
        Performs a dense vector similarity search.
        
        Args:
            query_embedding: Dense float vector of the user's query.
            collection_name: Target collection to search.
            filters: Optional ChromaDB metadata filter dict.
            top_k: Max number of results to return.
            
        Returns:
            A list of Chunk domain objects mapped from Chroma's result dictionary.
        """
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
        """
        Retrieves chunks purely based on metadata filters, ignoring vectors.
        
        Used primarily by the BM25 retriever to pull candidate documents
        before applying lexical scoring.
        
        Args:
            collection_name: Target collection.
            filters: ChromaDB metadata filter dict.
            
        Returns:
            A list of matching Chunk objects.
        """
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
