from typing import Optional, Dict
from datetime import datetime
from backend.core.domain.chat import ChatSession
from backend.core.interfaces.chat_session_repository import IChatSessionRepository

class MemoryChatSessionRepository(IChatSessionRepository):
    def __init__(self):
        self._sessions: Dict[str, ChatSession] = {}

    def save(self, session: ChatSession) -> None:
        session.updated_at = datetime.utcnow()
        self._sessions[session.session_id] = session

    def get(self, session_id: str) -> Optional[ChatSession]:
        return self._sessions.get(session_id)

    def delete(self, session_id: str) -> None:
        if session_id in self._sessions:
            del self._sessions[session_id]
