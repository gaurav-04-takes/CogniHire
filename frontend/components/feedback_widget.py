"""
Streamlit Component: Feedback Widget.

Architectural layer:
    Frontend (UI Components).

Purpose:
    Renders an interactive 1-5 star rating widget appended to AI chat responses,
    submitting feedback directly to the backend analytics service.
"""
import streamlit as st
import requests

def feedback_widget(session_id: str, message_index: int):
    """
    Renders a star rating selector and submits the user's rating for a specific chat interaction.
    """
    st.markdown("---")
    st.write("Rate this response:")
    cols = st.columns(5)
    
    for i in range(1, 6):
        with cols[i-1]:
            if st.button(f"{i} ⭐", key=f"star_{message_index}_{i}"):
                try:
                    payload = {
                        "session_id": session_id,
                        "score": i,
                        "comment": ""
                    }
                    response = requests.post("http://localhost:8000/api/v1/feedback", json=payload)
                    if response.status_code == 200:
                        st.success("Feedback submitted!")
                    else:
                        st.error("Failed to submit feedback.")
                except Exception as e:
                    st.error(f"Error: {e}")
