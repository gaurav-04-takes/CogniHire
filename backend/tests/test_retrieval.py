import pytest
from backend.application.dto.retrieval import RetrieveRequest
from backend.application.use_cases.retrieve_chunks import RetrieveRelevantChunksUseCase
from backend.infrastructure.retrievers.vector_retriever import VectorRetriever
from backend.infrastructure.retrievers.bm25_retriever import BM25Retriever
from backend.infrastructure.retrievers.hybrid_retriever import HybridRetriever
from backend.core.domain.chunk import Chunk
from backend.core.domain.document import DocumentType
from backend.core.interfaces.embedder import IEmbedder
from backend.core.interfaces.index_repository import IIndexRepository
from typing import List, Dict, Any, Optional

class MockEmbedder(IEmbedder):
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [[0.1] * 384 for _ in texts]

    def embed_query(self, query: str) -> List[float]:
        return [0.1] * 384

class MockIndexRepository(IIndexRepository):
    def __init__(self):
        self.chunks = [
            Chunk(
                id="chunk1", document_id="doc1", doc_type=DocumentType.RESUME,
                section_type="Skills", text="Python, Java, C++",
                metadata={"chunk_index": 0}
            ),
            Chunk(
                id="chunk2", document_id="doc2", doc_type=DocumentType.RESUME,
                section_type="Experience", text="Senior Engineer at Google",
                metadata={"chunk_index": 1}
            ),
            Chunk(
                id="chunk3", document_id="doc3", doc_type=DocumentType.JOB_DESCRIPTION,
                section_type="Requirements", text="Must know Python and Java",
                metadata={"chunk_index": 0}
            )
        ]
        
    def index_chunks(self, chunks: List[Chunk], collection_name: str) -> None:
        pass

    def delete_document(self, document_id: str, collection_name: str) -> None:
        pass

    def search(self, query_embedding: List[float], collection_name: str, filters: Optional[Dict[str, Any]] = None, top_k: int = 5) -> List[Chunk]:
        # Filter chunks mock logic
        filtered_chunks = []
        for chunk in self.chunks:
            # First check if collection matches doc_type roughly
            if collection_name == "resumes" and chunk.doc_type != DocumentType.RESUME:
                continue
            if collection_name == "job_descriptions" and chunk.doc_type != DocumentType.JOB_DESCRIPTION:
                continue
                
            if filters:
                match = True
                for k, v in filters.items():
                    if getattr(chunk, k, None) != v and chunk.metadata.get(k) != v:
                        match = False
                        break
                if not match:
                    continue
            filtered_chunks.append(chunk)
        return filtered_chunks[:top_k]

    def get_chunks(self, collection_name: str, filters: Optional[Dict[str, Any]] = None) -> List[Chunk]:
        return self.search(query_embedding=[], collection_name=collection_name, filters=filters, top_k=100)


def test_vector_retrieval():
    embedder = MockEmbedder()
    repo = MockIndexRepository()
    retriever = VectorRetriever(embedder, repo)
    use_case = RetrieveRelevantChunksUseCase(retriever)
    
    req = RetrieveRequest(query="software engineer", collection_name="resumes", top_k=2)
    res = use_case.execute(req)
    
    assert len(res.results) == 2
    assert res.query == "software engineer"
    assert res.results[0].document_type == "resume"

def test_metadata_filtering():
    embedder = MockEmbedder()
    repo = MockIndexRepository()
    retriever = VectorRetriever(embedder, repo)
    use_case = RetrieveRelevantChunksUseCase(retriever)
    
    # Filter by section title
    req = RetrieveRequest(
        query="python", 
        collection_name="resumes", 
        filters={"section_type": "Skills"}, 
        top_k=5
    )
    res = use_case.execute(req)
    
    assert len(res.results) == 1
    assert res.results[0].section_type == "Skills"
    assert res.results[0].chunk_id == "chunk1"

def test_top_k_behavior():
    embedder = MockEmbedder()
    repo = MockIndexRepository()
    retriever = VectorRetriever(embedder, repo)
    use_case = RetrieveRelevantChunksUseCase(retriever)
    
    # We have 2 resumes in the mock, setting top_k to 1 should return only 1
    req = RetrieveRequest(query="anything", collection_name="resumes", top_k=1)
    res = use_case.execute(req)
    
    assert len(res.results) == 1

def test_bm25_retrieval():
    repo = MockIndexRepository()
    retriever = BM25Retriever(repo)
    use_case = RetrieveRelevantChunksUseCase(retriever)
    
    # query for "Google", should match chunk2 "Senior Engineer at Google"
    req = RetrieveRequest(query="Google", collection_name="resumes", top_k=2)
    res = use_case.execute(req)
    
    assert len(res.results) == 1
    assert res.results[0].chunk_id == "chunk2"

def test_hybrid_retrieval():
    embedder = MockEmbedder()
    repo = MockIndexRepository()
    vector_retriever = VectorRetriever(embedder, repo)
    bm25_retriever = BM25Retriever(repo)
    hybrid_retriever = HybridRetriever(vector_retriever, bm25_retriever)
    use_case = RetrieveRelevantChunksUseCase(hybrid_retriever)
    
    # "software" vector matches all (mock always returns chunk1, chunk2), bm25 matches none
    # wait, bm25 query "Google" matches chunk2, vector matches chunk1 and chunk2
    req = RetrieveRequest(query="Google", collection_name="resumes", top_k=5)
    res = use_case.execute(req)
    
    # Hybrid should return 2 chunks: chunk1 and chunk2 interleaved/deduped
    assert len(res.results) == 2
    ids = {r.chunk_id for r in res.results}
    assert "chunk1" in ids
    assert "chunk2" in ids

