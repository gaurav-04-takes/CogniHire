from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any, List, Optional
from langchain_core.messages import BaseMessage

class ILLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate a complete response."""
        pass

    @abstractmethod
    async def stream(self, prompt: str, system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        """Stream a response token by token."""
        pass
        
    @abstractmethod
    async def chat(self, messages: List[BaseMessage]) -> BaseMessage:
        """Generate a response based on a history of messages."""
        pass
