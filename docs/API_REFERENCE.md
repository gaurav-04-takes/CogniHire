# CogniHire API Reference

Base URL: `http://localhost:8000/api/v1`

## Documents

### POST `/documents/upload`
Uploads a document (Resume or JD) for ingestion and embedding.
- **Form Data**:
  - `file`: The `.pdf` or `.docx` file (Max 10MB).
- **Response `200 OK`**:
  ```json
  {
    "document_id": "uuid",
    "status": "processing"
  }
  ```

### GET `/documents/{doc_id}/status`
Polls the processing status of a document.
- **Response `200 OK`**:
  ```json
  {
    "document_id": "uuid",
    "status": "completed",
    "chunks": 12,
    "indexed": true,
    "error": null
  }
  ```

## Analysis Endpoints

### POST `/analyze/match`
Calculates a weighted compatibility score between a Resume and a Job Description.
- **JSON Body**:
  ```json
  {
    "resume_id": "uuid",
    "jd_id": "uuid"
  }
  ```
- **Response `200 OK`**:
  ```json
  {
    "overall_score": 85,
    "skills": {"score": 90, "explanation": "..."},
    "experience": {"score": 80, "explanation": "..."},
    "education": {"score": 100, "explanation": "..."},
    "keywords": {"score": 75, "explanation": "..."},
    "explanation": "Strong candidate..."
  }
  ```

### POST `/analyze/ats`
Checks keyword compliance.
- **JSON Body**: Same as `/analyze/match`

### POST `/analyze/interview-questions`
Generates customized interview questions.
- **JSON Body**: Same as `/analyze/match`

## Chat Endpoints

### POST `/chat`
Ask a question against the embedded documents.
- **JSON Body**:
  ```json
  {
    "query": "Does the candidate know Kubernetes?",
    "session_id": "optional-uuid"
  }
  ```
- **Response `200 OK`**:
  ```json
  {
    "response": "Yes, they managed a Kubernetes cluster...",
    "session_id": "uuid",
    "citations": [
      {
        "document_id": "uuid",
        "section": "Experience",
        "text": "...managed a Kubernetes cluster..."
      }
    ]
  }
  ```

## Observability Endpoints

### GET `/analytics/metrics`
Returns system performance and RAG quality metrics.

### POST `/feedback`
Submit user feedback for an AI response.
- **JSON Body**:
  ```json
  {
    "session_id": "uuid",
    "score": 4
  }
  ```

### GET `/health/*`
Health checks for `/health/database`, `/health/vectorstore`, `/health/llm`, `/health/disk`, and `/health/evaluation`.
