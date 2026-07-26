"""
Streamlit Session State Manager.

Architectural layer:
    Frontend (State Management).

Purpose:
    Provides a typed, centralized interface for interacting with Streamlit's session_state.
    Ensures that required keys exist to prevent KeyError exceptions across pages.
"""
import streamlit as st
from typing import Any, Optional

class SessionManager:
    """
    Utility class for safely initializing and accessing Streamlit session state variables.
    """
    
    @staticmethod
    def init_state():
        """
        Initializes core state variables needed across the application if they do not exist.
        """
        if "selected_resume_id" not in st.session_state:
            st.session_state.selected_resume_id = None
        if "selected_jd_id" not in st.session_state:
            st.session_state.selected_jd_id = None
        if "chat_session_id" not in st.session_state:
            st.session_state.chat_session_id = None
        if "messages" not in st.session_state:
            st.session_state.messages = []

    @staticmethod
    def set(key: str, value: Any):
        """
        Sets a value in the Streamlit session state.
        """
        st.session_state[key] = value

    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """
        Retrieves a value from the Streamlit session state, returning a default if not found.
        """
        return st.session_state.get(key, default)

    @staticmethod
    def clear_chat():
        """
        Resets the active chat session ID and message history in the session state.
        """
        st.session_state.chat_session_id = None
        st.session_state.messages = []
