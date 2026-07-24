import streamlit as st
import time
from frontend.services.document_service import DocumentService
from frontend.state.session_manager import SessionManager

st.set_page_config(page_title="Upload Documents", page_icon="📄")
SessionManager.init_state()

st.title("Document Ingestion")

st.markdown("Upload resumes and job descriptions here. The system will automatically classify and process them.")

uploaded_files = st.file_uploader("Upload PDF or DOCX files", type=["pdf", "docx"], accept_multiple_files=True)

if uploaded_files:
    st.subheader("Classification Overrides")
    overrides = {}
    for file in uploaded_files:
        overrides[file.name] = st.selectbox(
            f"Select Type for {file.name}",
            options=["auto", "resume", "job_description"],
            format_func=lambda x: "Auto Detect" if x == "auto" else x.replace("_", " ").title(),
            key=f"override_{file.name}"
        )

    if st.button("Process Documents"):
        for file in uploaded_files:
            with st.spinner(f"Uploading {file.name}..."):
                try:
                    res = DocumentService.upload_document(file.getvalue(), file.name, doc_type=overrides[file.name])
                    doc_id = res.get("document_id")
                    
                    st.info(f"{file.name} uploaded. Processing...")
                    
                    # Polling
                    max_retries = 30
                    status_res = {}
                    for _ in range(max_retries):
                        time.sleep(2)
                        status_res = DocumentService.get_status(doc_id)
                        status = status_res.get("status")
                        if status in ["completed", "failed"]:
                            break
                            
                    status = status_res.get("status")
                    if status == "completed":
                        # Fetch final doc to get confidence
                        doc_info = DocumentService.get_document(doc_id)
                        dtype = doc_info.get("document_type", "unknown")
                        conf = doc_info.get("classification_confidence")
                        conf_str = f"{conf:.2f}" if conf is not None else "N/A"
                        
                        if dtype == "unknown":
                            st.warning(f"⚠️ {file.name} could not be automatically classified (Confidence: {conf_str}). It was not indexed.")
                            st.session_state[f"needs_classification_{doc_id}"] = True
                        else:
                            st.success(f"✅ {file.name} successfully processed as {dtype.upper()} (Confidence: {conf_str}).")
                    else:
                        st.error(f"❌ Failed to process {file.name}. Status: {status}")
                except Exception as e:
                    st.error(f"An error occurred with {file.name}: {str(e)}")

# Display pending classifications
st.divider()
st.subheader("Documents Pending Manual Classification")
docs = DocumentService.get_documents()
unknown_docs = [d for d in docs if d.get("document_type") == "unknown" and not d.get("indexed")]

if not unknown_docs:
    st.info("No documents are currently pending manual classification.")
else:
    for doc in unknown_docs:
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            st.write(f"**{doc.get('filename')}**")
            st.caption(f"Confidence: {doc.get('classification_confidence', 'N/A')}")
        with col2:
            selected_type = st.selectbox(
                "Select Document Type", 
                options=["resume", "job_description"], 
                key=f"select_{doc.get('id')}"
            )
        with col3:
            if st.button("Save & Index", key=f"btn_{doc.get('id')}"):
                with st.spinner("Reclassifying and indexing..."):
                    try:
                        DocumentService.reclassify_document(doc.get('id'), selected_type)
                        st.success(f"Reclassification started for {doc.get('filename')}.")
                        time.sleep(2) # Give it a moment before rerun
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
