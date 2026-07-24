import streamlit as st
import pandas as pd
from frontend.services.document_service import DocumentService

st.set_page_config(page_title="Document Management", page_icon="🗂️", layout="wide")

st.title("Document Management")

st.markdown("View and manage ingested documents.")

if st.button("Refresh"):
    st.rerun()

try:
    docs = DocumentService.get_documents()
    if docs:
        df = pd.DataFrame(docs)
        # Reorder columns
        df = df[["id", "filename", "document_type", "status", "chunk_count", "upload_date"]]
        st.dataframe(df, use_container_width=True)
        
        st.markdown("### Actions")
        doc_to_delete = st.selectbox("Select document to delete", options=[d["id"] for d in docs])
        if st.button("Delete Document"):
            try:
                DocumentService.delete_document(doc_to_delete)
                st.success(f"Document {doc_to_delete} deleted successfully.")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to delete document: {e}")
    else:
        st.info("No documents found.")
except Exception as e:
    st.error(f"Failed to load documents: {e}")
