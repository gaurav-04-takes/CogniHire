import pytest
import os
import shutil
from backend.infrastructure.vectorstores.chroma_repository import ChromaIndexRepository
from backend.core.domain.chunk import Chunk
from backend.core.domain.document import DocumentType

def test_chromadb_indexing():
    test_db_dir = "./test_chroma_db"
    if os.path.exists(test_db_dir):
        shutil.rmtree(test_db_dir, ignore_errors=True)
        
    try:
        # Pass None as embedder since we inject embeddings manually in pipeline
        repo = ChromaIndexRepository(persist_directory=test_db_dir, embedder=None)
        
        chunks = [
            Chunk(
                id="chunk1",
                document_id="doc1",
                doc_type=DocumentType.RESUME,
                section_type="Skills",
                text="Python, Java, C++",
                metadata={"embedding": [0.1, 0.2, 0.3], "document_id": "doc1", "document_type": "resume"}
            ),
            Chunk(
                id="chunk2",
                document_id="doc1",
                doc_type=DocumentType.RESUME,
                section_type="Experience",
                text="Software Engineer",
                metadata={"embedding": [0.4, 0.5, 0.6], "document_id": "doc1", "document_type": "resume"}
            )
        ]
        
        repo.index_chunks(chunks, "test_resumes")
        
        # Test Search
        results = repo.search([0.1, 0.2, 0.3], "test_resumes", top_k=1)
        assert len(results) == 1
        assert results[0].id == "chunk1"
        assert results[0].document_id == "doc1"
        
        # Test Delete
        repo.delete_document("doc1", "test_resumes")
        
        results_after_delete = repo.search([0.1, 0.2, 0.3], "test_resumes", top_k=1)
        assert len(results_after_delete) == 0
        
    finally:
        # Cleanup
        if os.path.exists(test_db_dir):
            try:
                # Close client connections first if possible, sometimes chromadb holds file locks
                shutil.rmtree(test_db_dir, ignore_errors=True)
            except:
                pass

def test_chromadb_get_chunks_and_exceptions():
    test_db_dir = "./test_chroma_db_2"
    if os.path.exists(test_db_dir):
        shutil.rmtree(test_db_dir, ignore_errors=True)
        
    try:
        repo = ChromaIndexRepository(persist_directory=test_db_dir, embedder=None)
        
        # Test empty chunks
        repo.index_chunks([], "test_coll")
        
        # Insert without embeddings
        chunks = [
            Chunk(
                id="chunk3",
                document_id="doc2",
                doc_type=DocumentType.RESUME,
                section_type="Skills",
                text="Python",
                metadata={"document_id": "doc2"}
            )
        ]
        repo.index_chunks(chunks, "test_coll")
        
        # Test get_chunks
        retrieved = repo.get_chunks("test_coll")
        assert len(retrieved) == 1
        assert retrieved[0].id == "chunk3"
        
        # Test search missing collection
        empty_res = repo.search([0.1], "missing_coll")
        assert empty_res == []
        
        # Test get_chunks missing collection
        empty_chunks = repo.get_chunks("missing_coll")
        assert empty_chunks == []
        
        # Test delete missing collection
        repo.delete_document("doc2", "missing_coll")
        
    finally:
        if os.path.exists(test_db_dir):
            shutil.rmtree(test_db_dir, ignore_errors=True)
