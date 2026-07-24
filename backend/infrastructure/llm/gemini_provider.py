from typing import AsyncGenerator, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from backend.core.interfaces.llm_provider import ILLMProvider
from backend.config.settings import settings

class GeminiProvider(ILLMProvider):
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
        try:
            response = await self.llm.ainvoke(messages)
            # Tracking token usage happens natively via LangSmith integration,
            # but response_metadata contains the token breakdown if needed:
            # response.response_metadata['token_usage']
            return response
        except Exception as e:
            raise RuntimeError(f"Gemini Chat API Error: {str(e)}")
