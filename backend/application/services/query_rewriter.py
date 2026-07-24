from typing import List
from langchain_core.messages import HumanMessage, SystemMessage
from backend.core.interfaces.llm_provider import ILLMProvider
from backend.core.domain.chat import ChatMessage
from backend.core.services.prompt_manager import PromptManager

class QueryRewriter:
    def __init__(self, llm_provider: ILLMProvider, prompt_manager: PromptManager):
        self.llm_provider = llm_provider
        self.prompt_manager = prompt_manager

    async def rewrite(self, query: str, history: List[ChatMessage]) -> str:
        """
        Rewrites the query using chat history to make it standalone.
        If no history exists, returns the query as is.
        """
        if not history:
            return query

        system_prompt = self.prompt_manager.get_prompt("query_rewriter")

        history_text = "\n".join([f"{msg.role}: {msg.content}" for msg in history[-5:]]) # Use last 5 messages
        
        prompt = f"Conversation History:\n{history_text}\n\nFollow-up question: {query}\n\nRewritten query:"
        
        rewritten_query = await self.llm_provider.generate(prompt=prompt, system_prompt=system_prompt)
        
        return rewritten_query.strip()
