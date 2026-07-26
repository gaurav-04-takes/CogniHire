"""
Google Gemini LLM provider implementation.

Architectural layer:
    Infrastructure.

Purpose:
    Implements ILLMProvider using the Google Generative AI (Gemini) API.
    Provides standard generation, streaming, and native chat capabilities.

Data flow:
    Accepts raw prompts or LangChain BaseMessages, translates them into
    Gemini API calls, and returns text or asynchronous generators.

Key dependencies:
    - langchain_google_genai
    - backend.core.interfaces.llm_provider

Side effects:
    - Makes external network requests to Google APIs.

Related modules:
    - backend.application.use_cases.chat_pipeline
    - backend.application.services.query_rewriter
"""
from typing import AsyncGenerator, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from backend.core.interfaces.llm_provider import ILLMProvider
from backend.config.settings import settings

class GeminiProvider(ILLMProvider):
    """
    LLM Provider for Google Gemini models via LangChain.
    """
    def __init__(self, 
                 model_name: Optional[str] = None, 
                 temperature: Optional[float] = None,
                 max_tokens: Optional[int] = None):
        
        # Pull from settings if not explicitly passed
        model = model_name or settings.GEMINI_MODEL
        temp = temperature if temperature is not None else settings.GEMINI_TEMPERATURE
        tokens = max_tokens or settings.GEMINI_MAX_TOKENS
        
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in environment configuration.")
            
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            temperature=temp,
            max_output_tokens=tokens,
            google_api_key=settings.GEMINI_API_KEY
        )

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Executes a single-turn completion call asynchronously.
        
        Args:
            prompt: User input string.
            system_prompt: Optional system instructions to guide behavior.
            
        Returns:
            The complete text response from the model.
            
        Raises:
            RuntimeError: If the Google API request fails.
        """
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))
        
        try:
            response = await self.llm.ainvoke(messages)
            content = response.content
            if isinstance(content, list):
                content_str = ""
                for item in content:
                    if isinstance(item, str):
                        content_str += item
                    elif isinstance(item, dict) and "text" in item:
                        content_str += item["text"]
                return content_str
            return str(content)
        except Exception as e:
            # Catch underlying google.api_core or requests exceptions and standardize
            raise RuntimeError(f"Gemini API Error: {str(e)}")

    async def stream(self, prompt: str, system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        """
        Executes a single-turn completion, yielding text chunks as they arrive.
        
        Args:
            prompt: User input string.
            system_prompt: Optional system instructions.
            
        Yields:
            String chunks of the model's response.
            
        Raises:
            RuntimeError: If the Google API request or streaming connection fails.
        """
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))
        
        try:
            async for chunk in self.llm.astream(messages):
                if chunk.content:
                    content = chunk.content
                    if isinstance(content, list):
                        content_str = ""
                        for item in content:
                            if isinstance(item, str):
                                content_str += item
                            elif isinstance(item, dict) and "text" in item:
                                content_str += item["text"]
                        yield content_str
                    else:
                        yield str(content)
        except Exception as e:
            raise RuntimeError(f"Gemini Streaming Error: {str(e)}")

    async def chat(self, messages: List[BaseMessage]) -> BaseMessage:
        """
        Executes a multi-turn chat completion using raw LangChain messages.
        
        Args:
            messages: A list of previously formatted LangChain message objects
                      (SystemMessage, HumanMessage, AIMessage).
                      
        Returns:
            The raw response object from the LLM.
        """
        try:
            response = await self.llm.ainvoke(messages)
            # Tracking token usage happens natively via LangSmith integration,
            # but response_metadata contains the token breakdown if needed:
            # response.response_metadata['token_usage']
            return response
        except Exception as e:
            raise RuntimeError(f"Gemini Chat API Error: {str(e)}")
