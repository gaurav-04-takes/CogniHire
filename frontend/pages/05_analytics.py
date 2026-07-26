"""
Streamlit Page: Analytics Dashboard.

Architectural layer:
    Frontend (UI Page).

Purpose:
    Displays high-level system metrics, quality evaluation scores (RAGAS), and
    document ingestion statistics using Plotly charts.
"""
import streamlit as st
import plotly.express as px
import pandas as pd
from frontend.services.document_service import DocumentService

st.set_page_config(page_title="Analytics", page_icon="📈", layout="wide")

st.title("System Analytics")

try:
    docs = DocumentService.get_documents()
    
    if docs:
        df = pd.DataFrame(docs)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Documents", len(df))
        col2.metric("Total Resumes", len(df[df["document_type"] == "resume"]))
        col3.metric("Total JDs", len(df[df["document_type"] == "job_description"]))
        
        st.divider()
        
        import requests
        try:
            metrics = requests.get("http://localhost:8000/api/v1/analytics/metrics").json()
            st.subheader("System Performance & Quality")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Avg Feedback", f"{metrics.get('average_feedback_score', 0)} / 5.0")
            m2.metric("Faithfulness", metrics.get('average_faithfulness', 0))
            m3.metric("Answer Relevancy", metrics.get('average_answer_relevancy', 0))
            m4.metric("Retrieval Latency", f"{metrics.get('recent_retrieval_latency_ms', 0)} ms")
        except Exception as e:
            st.warning(f"Could not load extended metrics: {e}")
            
        st.divider()
        
        st.subheader("Document Distribution")
        fig1 = px.pie(df, names='document_type', title='Document Types')
        st.plotly_chart(fig1, use_container_width=True)
        
        st.subheader("Processing Status")
        fig2 = px.bar(df['status'].value_counts().reset_index(), x='status', y='count', title='Status Counts')
        st.plotly_chart(fig2, use_container_width=True)
        
    else:
        st.info("No documents found to analyze.")

except Exception as e:
    st.error(f"Failed to load analytics: {e}")
