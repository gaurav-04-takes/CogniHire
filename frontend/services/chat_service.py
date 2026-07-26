"""
Frontend Chat Service.

Architectural layer:
    Frontend (Service Abstraction).

Purpose:
    Abstracts API calls to the backend `/chat` endpoints for standard chat,
    streaming chat, and history management.
"""
from typing import Dict, Any, Optional
from frontend.services.api_client import api_client

class ChatService:
    """
    Provides static methods to interact with the conversational RAG backend.
    """
    
    @staticmethod
    def chat(query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Sends a synchronous chat query and waits for the full response and citations.
        """
        payload = {"query": query, "session_id": session_id}
        return api_client.post("/chat", json=payload)

    @staticmethod
    def chat_stream(query: str, session_id: Optional[str] = None):
        """
        Sends a chat query and returns an iterable stream of Server-Sent Events (SSE).
        """
        payload = {"query": query, "session_id": session_id}
        return api_client.stream_post("/chat/stream", json=payload)

    @staticmethod
    def get_history(session_id: str) -> Dict[str, Any]:
        """
        Retrieves the complete message history for a given chat session ID.
        """
        return api_client.get(f"/chat/{session_id}/history")

    @staticmethod
    def delete_session(session_id: str) -> Dict[str, Any]:
        """
        Deletes a chat session from the backend.
        """
        return api_client.delete(f"/chat/{session_id}")
