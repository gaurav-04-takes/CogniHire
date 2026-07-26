"""
In-Memory Chat Session Repository.

Architectural layer:
    Infrastructure (Repository).

Purpose:
    Implements the IChatSessionRepository interface using a local Python dictionary.
    Useful for testing and ephemeral session tracking before transitioning to a
    persistent backend like Redis or a relational DB.

Data flow:
    Maps domain ChatSession objects to dictionary keys by session_id.

Key dependencies:
    - backend.core.interfaces.chat_session_repository.IChatSessionRepository

Side effects:
    - Mutates internal dict state in RAM. State is lost on application restart.

Related modules:
    - backend.core.domain.chat
"""
from typing import Optional, Dict
from datetime import datetime
from backend.core.domain.chat import ChatSession
from backend.core.interfaces.chat_session_repository import IChatSessionRepository

class MemoryChatSessionRepository(IChatSessionRepository):
    """
    Volatile storage implementation for chat history.
    """
    def __init__(self):
        self._sessions: Dict[str, ChatSession] = {}

    def save(self, session: ChatSession) -> None:
        """
        Persists the chat session to memory and updates the modified timestamp.
        """
        session.updated_at = datetime.utcnow()
        self._sessions[session.session_id] = session

    def get(self, session_id: str) -> Optional[ChatSession]:
        """
        Retrieves the chat session from memory.
        """
        return self._sessions.get(session_id)

    def delete(self, session_id: str) -> None:
        """
        Removes the chat session from memory if it exists.
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
