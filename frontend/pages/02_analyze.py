"""
Streamlit Page: Analysis Dashboard.

Architectural layer:
    Frontend (UI Page).

Purpose:
    Allows recruiters to select a processed resume and job description to generate
    and view detailed comparative AI analyses (match scores, skill gaps).
    Provides functionality to export the full report as PDF or JSON.
"""
import streamlit as st
from frontend.state.session_manager import SessionManager
from frontend.services.document_service import DocumentService
from frontend.services.analysis_service import AnalysisService
from frontend.components.match_score_widget import match_score_widget
from frontend.components.skill_gap_table import skill_gap_table
from frontend.components.citation_card import citation_card
import json
from fpdf import FPDF

st.set_page_config(page_title="Analysis Dashboard", page_icon="📊", layout="wide")
SessionManager.init_state()

st.title("Analysis Dashboard")

col_title, col_refresh = st.columns([0.8, 0.2])
with col_refresh:
    if st.button("Refresh Documents"):
        st.rerun()

try:
    docs = DocumentService.get_documents()
except Exception:
    st.error("Failed to fetch documents from API. Is the backend running?")
    st.stop()

resumes = [d for d in docs if d.get("document_type") == "resume" and d.get("status") == "completed" and d.get("indexed") == True]
jds = [d for d in docs if d.get("document_type") == "job_description" and d.get("status") == "completed" and d.get("indexed") == True]

col1, col2 = st.columns(2)

selected_resume = None
selected_jd = None

with col1:
    if not resumes:
        st.warning("No completed resumes are available. Upload a resume and wait for processing to finish.")
    else:
        # Preserve session state index
        resume_idx = 0
        saved_resume_id = SessionManager.get("selected_resume_id")
        for i, r in enumerate(resumes):
            if r["id"] == saved_resume_id:
                resume_idx = i
                break
                
        selected_resume = st.selectbox(
            "Select Resume", 
            options=resumes,
            index=resume_idx,
            format_func=lambda x: f"{x['filename']} (ID: {x['id'][:8]})"
        )
        if selected_resume:
            SessionManager.set("selected_resume_id", selected_resume["id"])

with col2:
    if not jds:
        st.warning("No completed job descriptions are available. Upload a job description and wait for processing to finish.")
    else:
        jd_idx = 0
        saved_jd_id = SessionManager.get("selected_jd_id")
        for i, j in enumerate(jds):
            if j["id"] == saved_jd_id:
                jd_idx = i
                break
                
        selected_jd = st.selectbox(
            "Select Job Description (Optional for some features)", 
            options=jds,
            index=jd_idx,
            format_func=lambda x: f"{x['filename']} (ID: {x['id'][:8]})"
        )
        if selected_jd:
            SessionManager.set("selected_jd_id", selected_jd["id"])

if st.button("Run Analysis"):
    if not selected_resume:
        st.warning("Please select a resume.")
    else:
        resume_id = selected_resume["id"]
        jd_id = selected_jd["id"] if selected_jd else None
        
        with st.spinner("Analyzing..."):
            try:
                summaries = AnalysisService.summary(resume_id, jd_id)
                SessionManager.set("summaries", summaries)
                
                if jd_id:
                    match_res = AnalysisService.match_score(resume_id, jd_id)
                    SessionManager.set("match_data", match_res)
                    
                    skills_res = AnalysisService.missing_skills(resume_id, jd_id)
                    SessionManager.set("skills_data", skills_res)
                    
                    ats_res = AnalysisService.ats_analysis(resume_id, jd_id)
                    SessionManager.set("ats_data", ats_res)
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")

summaries = SessionManager.get("summaries")
if summaries:
    st.divider()
    st.subheader("Document Summaries")
    s_col1, s_col2 = st.columns(2)
    with s_col1:
        st.markdown("**Resume Summary**")
        st.info(summaries["resume_summary"].get("summary", ""))
        citation_card(summaries["resume_summary"].get("citations", []))
    with s_col2:
        if "jd_summary" in summaries:
            st.markdown("**JD Summary**")
            st.info(summaries["jd_summary"].get("summary", ""))
            citation_card(summaries["jd_summary"].get("citations", []))

match_data = SessionManager.get("match_data")
skills_data = SessionManager.get("skills_data")
ats_data = SessionManager.get("ats_data")

if match_data and skills_data and ats_data:
    st.divider()
    match_score_widget(match_data)
    citation_card(match_data.get("citations", []))
    
    st.divider()
    skill_gap_table(skills_data, ats_data)
    
    st.divider()
    export_data = {
        "match": match_data,
        "skills": skills_data,
        "ats": ats_data
    }
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.download_button(
            label="Download Full Report (JSON)",
            data=json.dumps(export_data, indent=2),
            file_name="cognihire_report.json",
            mime="application/json"
        )
    with col_b:
        from frontend.services.export_service import ExportService
        try:
            pdf_bytes = ExportService.generate_pdf_report(export_data)
            st.download_button(
                label="Download Full Report (PDF)",
                data=pdf_bytes,
                file_name="cognihire_report.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Failed to generate PDF: {e}")
