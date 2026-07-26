"""
Streamlit Component: Skill Gap Table.

Architectural layer:
    Frontend (UI Components).

Purpose:
    Renders structured tables and lists detailing missing skills and ATS keyword analysis
    for a candidate compared to a job description.
"""
import streamlit as st
import pandas as pd

def skill_gap_table(skills_data: dict, ats_data: dict):
    """
    Renders pandas dataframes and markdown lists for skill gaps and ATS compatibility.
    """
    st.subheader("Skill Gap & ATS Analysis")
    
    missing_skills = skills_data.get("missing_skills", [])
    if missing_skills:
        st.markdown("### Missing Skills from JD")
        df = pd.DataFrame(missing_skills)
        st.dataframe(df, use_container_width=True)
    else:
        st.success("No missing skills detected based on the JD!")
        
    st.markdown("### ATS Keywords")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("Required Keywords")
        for kw in ats_data.get("required_keywords", []):
            st.write(f"- {kw}")
            
    with col2:
        st.success("Present Keywords")
        for kw in ats_data.get("present_keywords", []):
            st.write(f"- {kw}")
            
    with col3:
        st.error("Missing Keywords")
        for kw in ats_data.get("missing_keywords", []):
            st.write(f"- {kw}")
            
    if ats_data.get("recommendations"):
        st.markdown("**Recommendations:**")
        for rec in ats_data["recommendations"]:
            st.markdown(f"- {rec}")
