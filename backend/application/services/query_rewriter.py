"""
Query Rewriting Service.

Architectural layer:
    Application (Service).

Purpose:
    Modifies user conversational queries into standalone search queries using
    prior chat history. This prevents ambiguous pronouns (e.g., "what did he do?")
    from ruining vector retrieval performance.

Data flow:
    Takes the current query and past history, queries the LLM via PromptManager,
    and returns a resolved string.

Key dependencies:
    - backend.core.interfaces.llm_provider
    - backend.core.services.prompt_manager

Side effects:
    - Triggers an LLM completion request.

Related modules:
    - backend.application.use_cases.chat_pipeline
"""
from typing import List, Tuple
import json
from langchain_core.messages import HumanMessage, SystemMessage
from backend.core.interfaces.llm_provider import ILLMProvider
from backend.core.domain.chat import ChatMessage
from backend.core.services.prompt_manager import PromptManager

class QueryRewriter:
    """
    Service responsible for contextualizing user queries and detecting intent.
    """
    def __init__(self, llm_provider: ILLMProvider, prompt_manager: PromptManager):
        self.llm_provider = llm_provider
        self.prompt_manager = prompt_manager

    async def rewrite(self, query: str, history: List[ChatMessage]) -> Tuple[str, str]:
        """
        Rewrites the query using chat history to make it standalone and detects intent.
        
        Args:
            query: The latest user input string.
            history: The list of prior ChatMessage objects in the session.
            
        Returns:
            A tuple (intent, rewritten_query).
        """
        system_prompt = self.prompt_manager.get_prompt("query_rewriter")
        
        history_text = ""
        if history:
            history_text = "\n".join([f"{msg.role}: {msg.content}" for msg in history[-5:]]) # Use last 5 messages
            
        prompt = f"Conversation History:\n{history_text}\n\nFollow-up question: {query}\n\n"
        
        response = await self.llm_provider.generate(prompt=prompt, system_prompt=system_prompt)
        
        try:
            # Try to parse as JSON. Sometimes LLMs return markdown code blocks.
            import re
            json_str = response
            match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if match:
                json_str = match.group(1)
            parsed = json.loads(json_str)
            intent = parsed.get("intent", "comparison_explanation")
            rewritten_query = parsed.get("rewritten_query", query)
            return intent, rewritten_query
        except Exception:
            return "comparison_explanation", query
