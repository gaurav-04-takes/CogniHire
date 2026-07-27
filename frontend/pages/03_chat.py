"""
Streamlit Page: Chat Interface.

Architectural layer:
    Frontend (UI Page).

Purpose:
    Provides a ChatGPT-like conversational interface for querying ingested documents.
    Supports streaming responses, citation popovers, and inline feedback rating widgets.
"""
import streamlit as st
from frontend.state.session_manager import SessionManager
from frontend.services.chat_service import ChatService
from frontend.services.document_service import DocumentService
from frontend.components.citation_card import citation_card
from frontend.components.feedback_widget import feedback_widget

st.set_page_config(page_title="CogniHire Chat", page_icon="💬", layout="wide")
SessionManager.init_state()

st.title("CogniHire Chat")

# --- Document Selection ---
st.sidebar.header("Active Context")

@st.cache_data(ttl=5)
def get_processed_documents():
    docs = DocumentService.get_documents()
    resumes = [d for d in docs if d["document_type"] == "resume" and d["status"] == "completed" and d["indexed"]]
    jds = [d for d in docs if d["document_type"] == "job_description" and d["status"] == "completed" and d["indexed"]]
    return resumes, jds

resumes, jds = get_processed_documents()

resume_options = {d["id"]: d["filename"] for d in resumes}
jd_options = {d["id"]: d["filename"] for d in jds}

selected_resume_id = st.sidebar.selectbox(
    "Selected Resume:",
    options=list(resume_options.keys()),
    format_func=lambda x: resume_options.get(x, x),
    index=list(resume_options.keys()).index(SessionManager.get("selected_resume_id")) if SessionManager.get("selected_resume_id") in resume_options else 0 if resume_options else None
)

selected_jd_id = st.sidebar.selectbox(
    "Selected Job Description:",
    options=list(jd_options.keys()),
    format_func=lambda x: jd_options.get(x, x),
    index=list(jd_options.keys()).index(SessionManager.get("selected_jd_id")) if SessionManager.get("selected_jd_id") in jd_options else 0 if jd_options else None
)

# Handle context change
if selected_resume_id != SessionManager.get("selected_resume_id") or selected_jd_id != SessionManager.get("selected_jd_id"):
    SessionManager.set("selected_resume_id", selected_resume_id)
    SessionManager.set("selected_jd_id", selected_jd_id)
    SessionManager.clear_chat()
    st.rerun()

if st.sidebar.button("Clear Chat"):
    SessionManager.clear_chat()
    st.rerun()

# Quick Actions
st.sidebar.markdown("---")
st.sidebar.subheader("Quick Actions")
quick_actions = [
    "What should I change in my Resume?",
    "Show missing required skills",
    "Suggest ATS keyword improvements",
    "Improve my professional summary",
    "Highlight my most relevant experience",
    "Generate interview questions",
    "Explain my match score"
]

prompt = st.chat_input("Ask about the candidate...")

for action in quick_actions:
    if st.sidebar.button(action):
        prompt = action

if not selected_resume_id or not selected_jd_id:
    st.warning("Please select one completed Resume and one completed Job Description before requesting comparison or improvement guidance.")
else:
    # Display chat messages
    for i, msg in enumerate(SessionManager.get("messages", [])):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("citations"):
                citation_card(msg["citations"])
            if msg["role"] == "assistant":
                feedback_widget(SessionManager.get("chat_session_id", "default"), i)
    
    if prompt:
        # Add user message to state and display
        SessionManager.get("messages").append({"role": "user", "content": prompt, "citations": []})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                # Stream response
                session_id = SessionManager.get("chat_session_id")
                stream = ChatService.chat_stream(
                    prompt, 
                    session_id, 
                    resume_document_id=selected_resume_id, 
                    jd_document_id=selected_jd_id
                )
                
                for chunk in stream:
                    if chunk:
                        full_response += chunk
                        message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                
                # Update history
                SessionManager.get("messages").append({
                    "role": "assistant", 
                    "content": full_response, 
                    "citations": []
                })
                
            except Exception as e:
                st.error(f"Chat failed: {str(e)}")
