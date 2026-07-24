from typing import Dict, Any, Optional
from frontend.services.api_client import api_client

class ChatService:
    @staticmethod
    def chat(query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        payload = {"query": query, "session_id": session_id}
        return api_client.post("/chat", json=payload)

    @staticmethod
    def chat_stream(query: str, session_id: Optional[str] = None):
        payload = {"query": query, "session_id": session_id}
        return api_client.stream_post("/chat/stream", json=payload)

    @staticmethod
    def get_history(session_id: str) -> Dict[str, Any]:
        return api_client.get(f"/chat/{session_id}/history")

    @staticmethod
    def delete_session(session_id: str) -> Dict[str, Any]:
        return api_client.delete(f"/chat/{session_id}")
