import pytest
from typing import AsyncGenerator, List, Optional
from backend.core.domain.chunk import Chunk
from backend.core.domain.document import DocumentType
from backend.core.interfaces.llm_provider import ILLMProvider
from backend.core.interfaces.retriever import IRetriever
from backend.core.interfaces.reranker import IReranker
from backend.core.domain.chat import ChatMessage
from backend.infrastructure.retrievers.rrf_retriever import RRFRetriever
from backend.infrastructure.rerankers.bge_reranker import BGEReranker
from backend.application.services.query_rewriter import QueryRewriter
from backend.application.services.context_builder import ContextBuilder
from backend.infrastructure.repositories.memory_chat_session_repository import MemoryChatSessionRepository
from backend.application.use_cases.chat_pipeline import ChatPipelineUseCase

class MockLLMProvider(ILLMProvider):
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if "Follow-up question:" in prompt:
            return '{"intent": "comparison_explanation", "rewritten_query": "rewritten query"}'
        return "mocked answer"

    async def stream(self, prompt: str, system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        yield "mocked answer"

    async def chat(self, messages: List[any]) -> any:
        pass

class MockRetriever(IRetriever):
    def __init__(self, chunks: List[Chunk]):
        self.chunks = chunks

    def retrieve(self, query: str, collection_name: str, filters=None, top_k=5) -> List[Chunk]:
        return self.chunks[:top_k]

def test_rrf_ranking():
    # Setup mock chunks
    c1 = Chunk(id="c1", document_id="doc1", doc_type=DocumentType.RESUME, text="A", metadata={})
    c2 = Chunk(id="c2", document_id="doc1", doc_type=DocumentType.RESUME, text="B", metadata={})
    c3 = Chunk(id="c3", document_id="doc1", doc_type=DocumentType.RESUME, text="C", metadata={})
    
    # retriever1 returns c1, c2
    ret1 = MockRetriever([c1, c2])
    # retriever2 returns c2, c3
    ret2 = MockRetriever([c2, c3])
    
    rrf = RRFRetriever(ret1, ret2, k=1)
    results = rrf.retrieve("query", "col")
    
    # c2 is in both, should be ranked 1st
    assert results[0].id == "c2"

def test_context_builder_and_citations():
    builder = ContextBuilder()
    c = Chunk(id="c1", document_id="doc1", doc_type=DocumentType.RESUME, section_type="Experience", text="Content", metadata={"page": 1, "chunk_index": 2})
    
    context_str, citations = builder.build_context([c])
    
    assert "Resume | Experience | Page 1 | Chunk 2" in context_str
    assert citations[0].document_id == "doc1"
    assert citations[0].page == 1

class MockPromptManager:
    def get_prompt(self, prompt_key: str, **kwargs) -> str:
        return f"Mocked system prompt for {prompt_key}"

@pytest.mark.asyncio
async def test_query_rewriter():
    rewriter = QueryRewriter(MockLLMProvider(), MockPromptManager())
    history = [ChatMessage(role="user", content="hi"), ChatMessage(role="assistant", content="hello")]
    
    rewritten_tuple = await rewriter.rewrite("tell me more", history)
    assert rewritten_tuple[1] == "rewritten query"

class MockReranker(IReranker):
    def rerank(self, query: str, chunks: List[Chunk], top_k: int = 5) -> List[Chunk]:
        # Just return chunks as is, possibly assigned a mock score
        for i, c in enumerate(chunks):
            c.score = 1.0 / (i + 1)
        return chunks[:top_k]

@pytest.mark.asyncio
async def test_chat_pipeline():
    c = Chunk(id="c1", document_id="doc1", doc_type=DocumentType.RESUME, section_type="Exp", text="Data", metadata={})
    
    pipeline = ChatPipelineUseCase(
        retriever=MockRetriever([c]),
        reranker=MockReranker(),
        llm_provider=MockLLMProvider(),
        session_repository=MemoryChatSessionRepository(),
        query_rewriter=QueryRewriter(MockLLMProvider(), MockPromptManager()),
        context_builder=ContextBuilder(),
        prompt_manager=MockPromptManager()
    )
    
    response_text, msg, session = await pipeline.execute("query")
    
    assert response_text == "mocked answer"
    assert len(session.history) == 2 # 1 user, 1 assistant
    assert session.rewritten_queries[0] == "rewritten query"
