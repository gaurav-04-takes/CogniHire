import streamlit as st

def citation_card(citations: list):
    if not citations:
        return
        
    with st.expander("View Citations", expanded=False):
        for idx, citation in enumerate(citations):
            if isinstance(citation, dict):
                formatted = f"[{citation.get('document_id')} | {citation.get('section_type')} | Chunk {citation.get('chunk_index')}]"
                st.markdown(f"**Source {idx+1}:** {formatted}")
                if 'text' in citation:
                    st.info(citation['text'])
            else:
                st.markdown(f"**Source {idx+1}:** {citation}")
