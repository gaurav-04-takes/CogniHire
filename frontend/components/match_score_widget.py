"""
Streamlit Component: Match Score Widget.

Architectural layer:
    Frontend (UI Components).

Purpose:
    Renders a visual representation of a candidate's match score against a job description,
    including a top-level gauge chart and metric breakdowns for specific dimensions.
"""
import streamlit as st
import plotly.graph_objects as go

def match_score_widget(match_data: dict):
    """
    Renders the overall match score gauge and dimensional score columns.
    """
    st.subheader("Match Score Analysis")
    
    overall = match_data.get("overall_score", 0)
    
    # Plotly Gauge Chart for Overall Score
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = overall,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Overall Match Score"},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 80], 'color': "gray"}
            ]
        }
    ))
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown(f"**Explanation:** {match_data.get('explanation', '')}")
    
    st.markdown("### Dimension Breakdown")
    col1, col2, col3, col4 = st.columns(4)
    
    def render_dim(col, title, data):
        with col:
            score = data.get("score", 0)
            st.metric(title, f"{score}%")
            with st.expander("Details"):
                st.write(data.get("explanation", ""))
    
    render_dim(col1, "Skills (40%)", match_data.get("skills", {}))
    render_dim(col2, "Experience (30%)", match_data.get("experience", {}))
    render_dim(col3, "Education (15%)", match_data.get("education", {}))
    render_dim(col4, "Keywords (15%)", match_data.get("keywords", {}))
