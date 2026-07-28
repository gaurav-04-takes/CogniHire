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

    async def execute(self, query: str, session_id: Optional[str] = None, resume_document_id: Optional[str] = None, jd_document_id: Optional[str] = None, collection_name: str = "documents") -> Tuple[str, ChatMessage, ChatSession]:
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
            session = ChatSession(session_id=session_id, resume_document_id=resume_document_id, jd_document_id=jd_document_id)
            self.session_repository.save(session)
        else:
            session = self.session_repository.get(session_id)
            if not session:
                session = ChatSession(session_id=session_id, resume_document_id=resume_document_id, jd_document_id=jd_document_id)
                self.session_repository.save(session)
            elif session.resume_document_id != resume_document_id or session.jd_document_id != jd_document_id:
                # Context changed, reset history
                session.history = []
                session.rewritten_queries = []
                session.resume_document_id = resume_document_id
                session.jd_document_id = jd_document_id
                self.session_repository.save(session)
                
        # 1. Rewrite Query
        try:
            intent, rewritten_query = await self.query_rewriter.rewrite(query, session.history)
        except Exception as e:
            from backend.core.domain.exceptions import LLMProviderError
            raise LLMProviderError(f"Failed to rewrite query: {str(e)}")
            
        session.rewritten_queries.append(rewritten_query)
        
        # Add user message to history
        user_msg = ChatMessage(role="user", content=query)
        session.history.append(user_msg)
        
        # 2. Retrieve (with cache)
        cache_key = f"retrieve_{rewritten_query}_{collection_name}_{resume_document_id}_{jd_document_id}"
        retrieved_chunks = cache_service.get(cache_key)
        
        filters = None
        if resume_document_id and jd_document_id:
            filters = {
                "$or": [
                    {"document_id": resume_document_id},
                    {"document_id": jd_document_id}
                ]
            }
        
        if not retrieved_chunks:
            retrieved_chunks = self.retriever.retrieve(rewritten_query, collection_name=collection_name, filters=filters, top_k=20)
            cache_service.set(cache_key, retrieved_chunks, ttl_seconds=300) # Cache for 5 mins
        
        # 3. Rerank
        reranked_chunks = self.reranker.rerank(rewritten_query, retrieved_chunks, top_k=5)
        
        # 4. Build Context
        context_str, citations = self.context_builder.build_context(reranked_chunks)
        
        # 5. Generate Response
        if intent == "resume_improvement":
            system_prompt = self.prompt_manager.get_prompt("resume_improvement", context_str=context_str)
        else:
            system_prompt = self.prompt_manager.get_prompt("chat_generation", context_str=context_str)
        
        try:
            response_text = await self.llm_provider.generate(prompt=query, system_prompt=system_prompt)
        except Exception as e:
            from backend.core.domain.exceptions import LLMProviderError
            if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
                raise LLMProviderError("The AI service is currently rate-limited. Please wait a few seconds and try again.")
            raise LLMProviderError(f"Failed to generate response: {str(e)}")
        
        if intent == "resume_improvement":
            import json, re
            try:
                json_str = response_text
                match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
                if match:
                    json_str = match.group(1)
                parsed = json.loads(json_str)
                # Convert structured JSON to Markdown
                md_response = f"### Resume-JD Alignment Summary\n{parsed.get('alignment_summary', '')}\n\n"
                
                high_priority = parsed.get('high_priority_changes', [])
                if high_priority:
                    md_response += "### High-Priority Changes\n"
                    for change in high_priority:
                        md_response += f"- **{change.get('section', 'General')} ({change.get('priority', 'Medium')} Priority)**:\n"
                        md_response += f"  - **JD Requirement**: {change.get('jd_requirement', '')}\n"
                        md_response += f"  - **Current Resume**: {change.get('current_resume_evidence', '')}\n"
                        md_response += f"  - **Recommendation**: {change.get('recommendation', '')}\n"
                        md_response += f"  - *Rationale*: {change.get('rationale', '')}\n"
                        
                md_response += f"\n\n*Disclaimer: {parsed.get('disclaimer', '')}*"
                response_text = md_response
            except Exception as e:
                response_text = "I encountered an error formatting the improvement recommendations. Here is the raw output:\n\n" + response_text
        
        # 6. Attach Citations and Save Session
        assistant_msg = ChatMessage(role="assistant", content=response_text, citations=citations)
        session.history.append(assistant_msg)
        self.session_repository.save(session)
        
        return response_text, assistant_msg, session

    async def execute_stream(self, query: str, session_id: Optional[str] = None, resume_document_id: Optional[str] = None, jd_document_id: Optional[str] = None, collection_name: str = "documents") -> AsyncGenerator[str, None]:
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
            session = ChatSession(session_id=session_id, resume_document_id=resume_document_id, jd_document_id=jd_document_id)
            self.session_repository.save(session)
        else:
            session = self.session_repository.get(session_id)
            if not session:
                session = ChatSession(session_id=session_id, resume_document_id=resume_document_id, jd_document_id=jd_document_id)
                self.session_repository.save(session)
            elif session.resume_document_id != resume_document_id or session.jd_document_id != jd_document_id:
                session.history = []
                session.rewritten_queries = []
                session.resume_document_id = resume_document_id
                session.jd_document_id = jd_document_id
                self.session_repository.save(session)
                
        try:
            intent, rewritten_query = await self.query_rewriter.rewrite(query, session.history)
        except Exception as e:
            if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
                yield "I'm sorry, the AI service is currently rate-limited. Please wait a few seconds and try again."
            else:
                yield f"An error occurred while processing your request: {str(e)}"
            return
            
        session.rewritten_queries.append(rewritten_query)
        
        user_msg = ChatMessage(role="user", content=query)
        session.history.append(user_msg)
        
        filters = None
        if resume_document_id and jd_document_id:
            filters = {
                "$or": [
                    {"document_id": resume_document_id},
                    {"document_id": jd_document_id}
                ]
            }
            
        retrieved_chunks = self.retriever.retrieve(rewritten_query, collection_name=collection_name, filters=filters, top_k=20)
        reranked_chunks = self.reranker.rerank(rewritten_query, retrieved_chunks, top_k=5)
        
        context_str, citations = self.context_builder.build_context(reranked_chunks)
        
        if intent == "resume_improvement":
            system_prompt = self.prompt_manager.get_prompt("resume_improvement", context_str=context_str)
        else:
            system_prompt = self.prompt_manager.get_prompt("chat_generation", context_str=context_str)
        
        full_response = ""
        try:
            async for chunk in self.llm_provider.stream(prompt=query, system_prompt=system_prompt):
                full_response += chunk
                yield chunk
        except Exception as e:
            error_msg = ""
            if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
                error_msg = "\n\n[Error: The AI service is currently rate-limited. Please wait a few seconds and try again.]"
            else:
                error_msg = f"\n\n[An error occurred during generation: {str(e)}]"
            full_response += error_msg
            yield error_msg
            
        assistant_msg = ChatMessage(role="assistant", content=full_response, citations=citations)
        session.history.append(assistant_msg)
        self.session_repository.save(session)
