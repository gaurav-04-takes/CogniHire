import streamlit as st
from typing import Any, Optional

class SessionManager:
    @staticmethod
    def init_state():
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
        st.session_state[key] = value

    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        return st.session_state.get(key, default)

    @staticmethod
    def clear_chat():
        st.session_state.chat_session_id = None
        st.session_state.messages = []
