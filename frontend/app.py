import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from frontend.state.session_manager import SessionManager

st.set_page_config(
    page_title="CogniHire",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

SessionManager.init_state()

st.title("CogniHire - Hiring Intelligence")

st.markdown("""
Welcome to **CogniHire**, the next-generation Hiring Intelligence platform.

Please select a tool from the sidebar to begin.
- **Upload**: Ingest Resumes and Job Descriptions
- **Analyze**: See Match Scores, Skill Gaps, and ATS Analysis
- **Chat**: Discuss candidates and ask specific questions
- **Documents**: Manage ingested documents
- **Analytics**: View operational metrics
""")

st.sidebar.info("Select a page above.")
