"""
RAG Chat Pipeline Use Case.

Architectural layer:
    Application (Use Case)

Purpose:
    Orchestrates the entire Retrieval-Augmented Generation (RAG) chat workflow.
    Coordinates query rewriting, caching, retrieval, reranking, context building,
    and LLM generation into a single cohesive process.

Data flow:
    User query -> QueryRewriter -> Cache check -> Retriever -> Reranker -> 
    ContextBuilder -> LLM Provider -> ChatSession persistence.

Key dependencies:
    - backend.core.interfaces.retriever
    - backend.core.interfaces.llm_provider
    - backend.application.services.query_rewriter
    - backend.application.services.context_builder

Side effects:
    - Calls external LLM APIs.
    - Mutates and saves state to ChatSessionRepository.
    - Updates the Redis cache.

Related modules:
    - backend.api.chat
"""
from typing import Optional, AsyncGenerator, Tuple
from backend.core.interfaces.retriever import IRetriever
from backend.core.interfaces.reranker import IReranker
from backend.core.interfaces.llm_provider import ILLMProvider
from backend.core.interfaces.chat_session_repository import IChatSessionRepository
from backend.application.services.query_rewriter import QueryRewriter
from backend.application.services.context_builder import ContextBuilder
from backend.core.domain.chat import ChatSession, ChatMessage
from backend.core.services.prompt_manager import PromptManager
from backend.core.services.cache_service import cache_service
import uuid

class ChatPipelineUseCase:
    """
    Coordinator for the conversational RAG pipeline.
    """
    def __init__(
        self,
        retriever: IRetriever,
        reranker: IReranker,
        llm_provider: ILLMProvider,
        session_repository: IChatSessionRepository,
        query_rewriter: QueryRewriter,
        context_builder: ContextBuilder,
        prompt_manager: PromptManager
    ):
        self.retriever = retriever
        self.reranker = reranker
        self.llm_provider = llm_provider
        self.session_repository = session_repository
        self.query_rewriter = query_rewriter
        self.context_builder = context_builder
        self.prompt_manager = prompt_manager

    async def execute(self, query: str, session_id: Optional[str] = None, collection_name: str = "documents") -> Tuple[str, ChatMessage, ChatSession]:
        """
        Executes the full RAG chat pipeline and returns the full response, the assistant message, and the session.
        
        Workflow:
        1. Resumes or creates a ChatSession.
        2. Rewrites the query using history for better retrieval context.
        3. Retrieves chunks (using a 5-minute cache).
        4. Reranks chunks to improve precision.
        5. Formats chunks into an LLM context string.
        6. Generates a response using the LLM.
        7. Saves the updated session history.
        
        Args:
            query: The user's input message.
            session_id: Optional UUID to resume a conversation.
            collection_name: The Chroma collection to search.
            
        Returns:
            A tuple containing:
                - The raw response string.
                - The ChatMessage domain object representing the assistant's reply (with citations).
                - The updated ChatSession domain object.
        """
        if not session_id:
            session_id = str(uuid.uuid4())
            session = ChatSession(session_id=session_id)
            self.session_repository.save(session)
        else:
            session = self.session_repository.get(session_id)
            if not session:
                session = ChatSession(session_id=session_id)
                self.session_repository.save(session)
                
        # 1. Rewrite Query
        rewritten_query = await self.query_rewriter.rewrite(query, session.history)
        session.rewritten_queries.append(rewritten_query)
        
        # Add user message to history
        user_msg = ChatMessage(role="user", content=query)
        session.history.append(user_msg)
        
        # 2. Retrieve (with cache)
        cache_key = f"retrieve_{rewritten_query}_{collection_name}"
        retrieved_chunks = cache_service.get(cache_key)
        
        if not retrieved_chunks:
            retrieved_chunks = self.retriever.retrieve(rewritten_query, collection_name=collection_name, top_k=20)
            cache_service.set(cache_key, retrieved_chunks, ttl_seconds=300) # Cache for 5 mins
        
        # 3. Rerank
        reranked_chunks = self.reranker.rerank(rewritten_query, retrieved_chunks, top_k=5)
        
        # 4. Build Context
        context_str, citations = self.context_builder.build_context(reranked_chunks)
        
        # 5. Generate Response
        system_prompt = self.prompt_manager.get_prompt("chat_generation", context_str=context_str)
        
        response_text = await self.llm_provider.generate(prompt=query, system_prompt=system_prompt)
        
        # 6. Attach Citations and Save Session
        assistant_msg = ChatMessage(role="assistant", content=response_text, citations=citations)
        session.history.append(assistant_msg)
        self.session_repository.save(session)
        
        return response_text, assistant_msg, session

    async def execute_stream(self, query: str, session_id: Optional[str] = None, collection_name: str = "documents") -> AsyncGenerator[str, None]:
        """
        Executes the RAG pipeline but yields the response text token by token.
        (Note: Saving citations requires collecting the full response, so it's simplified here).
        
        Args:
            query: User input message.
            session_id: Optional UUID.
            collection_name: Target vector collection.
            
        Yields:
            String fragments of the LLM's response as they stream in.
        """
        if not session_id:
            session_id = str(uuid.uuid4())
            session = ChatSession(session_id=session_id)
            self.session_repository.save(session)
        else:
            session = self.session_repository.get(session_id)
            if not session:
                session = ChatSession(session_id=session_id)
                self.session_repository.save(session)
                
        rewritten_query = await self.query_rewriter.rewrite(query, session.history)
        session.rewritten_queries.append(rewritten_query)
        
        user_msg = ChatMessage(role="user", content=query)
        session.history.append(user_msg)
        
        retrieved_chunks = self.retriever.retrieve(rewritten_query, collection_name=collection_name, top_k=20)
        reranked_chunks = self.reranker.rerank(rewritten_query, retrieved_chunks, top_k=5)
        
        context_str, citations = self.context_builder.build_context(reranked_chunks)
        
        system_prompt = self.prompt_manager.get_prompt("chat_generation", context_str=context_str)
        
        full_response = ""
        async for chunk in self.llm_provider.stream(prompt=query, system_prompt=system_prompt):
            full_response += chunk
            yield chunk
            
        assistant_msg = ChatMessage(role="assistant", content=full_response, citations=citations)
        session.history.append(assistant_msg)
        self.session_repository.save(session)
