from abc import ABC, abstractmethod
from typing import Optional
from backend.core.domain.chat import ChatSession

class IChatSessionRepository(ABC):
    @abstractmethod
    def save(self, session: ChatSession) -> None:
        """Save or update a chat session."""
        pass

    @abstractmethod
    def get(self, session_id: str) -> Optional[ChatSession]:
        """Retrieve a chat session by its ID."""
        pass

    @abstractmethod
    def delete(self, session_id: str) -> None:
        """Delete a chat session by its ID."""
        pass
