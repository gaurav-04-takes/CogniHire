# CogniHire

![CogniHire Logo Placeholder](https://via.placeholder.com/800x200?text=CogniHire+-+AI+Hiring+Intelligence)

## Project Overview

CogniHire is a state-of-the-art AI-powered hiring intelligence platform designed to streamline the recruitment process. By leveraging a highly decoupled Clean Architecture and advanced Retrieval-Augmented Generation (RAG), CogniHire ingests candidate resumes and job descriptions (JDs), extracting meaningful insights to automate matching, skill gap analysis, and interview preparation.

## Business Problem

Recruiters spend countless hours manually cross-referencing resumes against dense job descriptions. Traditional Applicant Tracking Systems (ATS) rely heavily on exact keyword matching, unfairly filtering out qualified candidates who use different terminology (e.g., "React Engineer" vs "Frontend Developer"). CogniHire solves this by utilizing **semantic understanding**—evaluating candidates based on the actual meaning and context of their experience rather than rigid keyword lists.

## Architecture & Features

CogniHire is built using Python, FastAPI, Streamlit, ChromaDB, and Google Gemini API. 

**Core Features:**
- **Advanced Document Ingestion:** Intelligent section-aware chunking for PDFs and DOCX files.
- **Hybrid Retrieval (RRF):** Merges Semantic (Vector) search with Lexical (BM25) search for optimal recall, boosted by a Cross-Encoder Reranker.
- **Hiring Intelligence APIs:** Generates exact Match Scores, Skill Gaps, and tailored Interview Questions based on deep resume-to-JD comparisons.
- **Conversational Engine:** A citation-backed chat interface allowing recruiters to interact directly with the candidate's parsed context.
- **Enterprise Observability:** Fully instrumented with structured JSON logging, LangSmith tracing, and Ragas-based quality evaluations.

---

## Installation Guide

### Prerequisites
1. **Python 3.10+**
2. **Google Gemini API Key**: You must obtain an API key from Google AI Studio.
3. **BGE Embedding Model**: Ensure you have local embeddings setup or a cloud embedding model configured.

### Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/CogniHire.git
   cd CogniHire
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   *(Note: Add your actual `requirements.txt` installation step here)*
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Create a `.env` file in the root directory:
   ```env
   ENVIRONMENT=development
   APP_NAME="CogniHire API"
   CORS_ORIGINS="*"
   MAX_UPLOAD_SIZE_MB=10
   CACHE_TYPE=memory
   GEMINI_API_KEY="your_google_gemini_api_key_here"
   ```

### Step-by-Step: Enabling LangSmith Observability

To gain deep insights, trace LLM latency, and debug prompt chains, you can enable LangSmith.

1. **Sign up for LangSmith:** Go to [smith.langchain.com](https://smith.langchain.com/) and create a free account.
2. **Generate an API Key:** 
   - Navigate to **Settings** (gear icon) -> **API Keys**.
   - Click **Create API Key**.
   - Copy the generated key.
3. **Add to `.env`:** Add the following lines to your `.env` file:
   ```env
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY="your_api_key_here"
   LANGCHAIN_PROJECT="CogniHire_Local"
   ```
4. *Restart your backend.* All LLM calls and retrieval traces will now appear in your LangSmith dashboard!

---

## Example Usage

### Running the Backend (FastAPI)
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```
Navigate to `http://localhost:8000/docs` to view the interactive Swagger UI.

### Running the Frontend (Streamlit)
Open a new terminal window:
```bash
streamlit run frontend/main.py
```
This will launch the web dashboard where you can upload documents, view analytics, and chat with the AI.

## Future Enhancements
- Kubernetes deployment manifests (Helm charts).
- Transitioning from SQLite to PostgreSQL for production data persistence.
- Implementing Celery / Redis for distributed asynchronous document ingestion.
