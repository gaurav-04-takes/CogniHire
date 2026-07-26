"""
Language model provider interface.

Architectural layer:
    Core interfaces.

Purpose:
    Defines the provider-independent contract for language-model access.

Data flow:
    Application services send prompts to this interface and receive
    generated text back, isolating them from specific LLM APIs.

Key dependencies:
    - langchain_core.messages.BaseMessage

Related modules:
    - backend.infrastructure.llm.gemini_provider
"""
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any, List, Optional
from langchain_core.messages import BaseMessage

class ILLMProvider(ABC):
    """
    Defines the provider-independent contract for language-model access.

    Application services depend on this interface instead of the Google
    Gemini SDK. This separation allowed the previous local provider to be
    replaced with Gemini without changing the RAG or hiring-analysis logic.

    Current implementation:
        GeminiProvider

    Implementations must support standard generation and asynchronous
    streaming while translating provider-specific failures into application
    exceptions.
    """
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate a complete response.

        Args:
            prompt: The user query or task instruction.
            system_prompt: Optional system-level instructions for the model.

        Returns:
            The generated string response.
            
        Raises:
            LLMGenerationError: If the provider fails to generate a response.
        """
        pass

    @abstractmethod
    async def stream(self, prompt: str, system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        """
        Stream a response token by token.

        Args:
            prompt: The user query or task instruction.
            system_prompt: Optional system-level instructions for the model.

        Returns:
            An asynchronous generator yielding text chunks as they are generated.
        """
        pass
        
    @abstractmethod
    async def chat(self, messages: List[BaseMessage]) -> BaseMessage:
        """
        Generate a response based on a history of messages.

        Args:
            messages: A list of LangChain BaseMessage objects representing the conversation.

        Returns:
            The generated response as a BaseMessage.
        """
        pass
