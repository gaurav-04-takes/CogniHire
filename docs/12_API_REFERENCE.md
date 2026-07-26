# 12 — API Reference

All endpoints are prefixed with `/api/v1`.

---

## Documents API (`/documents`)

### Upload Document
`POST /documents/upload`
- **Content-Type**: `multipart/form-data`
- **Body**: 
  - `file`: The document (PDF/DOCX)
  - `document_type`: string, default "auto" (options: "auto", "resume", "job_description")
- **Response**: `202 Accepted`
  ```json
  {
    "document_id": "uuid",
    "status": "processing"
  }
  ```

### List Documents
`GET /documents`
- **Response**: `200 OK`
  ```json
  {
    "documents": [
      {
        "id": "uuid",
        "filename": "resume.pdf",
        "doc_type": "resume",
        "status": "COMPLETED",
        "indexed": true,
        "chunks_count": 5,
        "uploaded_at": "2024-01-01T00:00:00"
      }
    ]
  }
  ```

### Get Document Status
`GET /documents/{doc_id}/status`
- **Response**: `200 OK`
  ```json
  {
    "document_id": "uuid",
    "status": "COMPLETED",
    "indexed": true,
    "chunks_count": 5,
    "doc_type": "resume",
    "error_message": null
  }
  ```

### Get Document Metadata
`GET /documents/{doc_id}`
- **Response**: `200 OK`
  Returns `DocumentItemDTO` (same as list item).

### Reclassify Document
`POST /documents/{doc_id}/reclassify`
- **Content-Type**: `application/json`
- **Body**: `{"document_type": "resume"}`
- **Response**: `202 Accepted`
  ```json
  {
    "document_id": "uuid",
    "status": "reprocessing"
  }
  ```

### Delete Document
`DELETE /documents/{doc_id}`
- **Response**: `200 OK`
  ```json
  {
    "status": "deleted"
  }
  ```

---

## Analysis API (`/analyze`)

All endpoints in this group accept the same request schema and validate document states before executing.

**Common Request Schema (`AnalysisRequest`)**:
```json
{
  "resume_id": "uuid_of_resume",
  "jd_id": "uuid_of_jd"  // Optional for summary, required for others
}
```

### Match Score
`POST /analyze/match`
Returns `MatchScoreResponse`.

### Missing Skills
`POST /analyze/skills`
Returns `MissingSkillsResponse`.

### ATS Analysis
`POST /analyze/ats`
Returns `ATSAnalysisResponse`.

### Interview Questions
`POST /analyze/interview-questions`
Returns `InterviewQuestionResponse`.

### Summary
`POST /analyze/summary`
Returns `SummaryResponse` (includes JD summary if jd_id provided).

---

## Chat API (`/chat`)

### Synchronous Chat
`POST /chat`
- **Body**:
  ```json
  {
    "query": "What is his experience?",
    "session_id": "optional_uuid"
  }
  ```
- **Response**:
  ```json
  {
    "session_id": "uuid",
    "response": "He has 5 years of...",
    "citations": [
      {
        "document_id": "uuid",
        "document_type": "resume",
        "section_type": "Experience",
        "chunk_index": 2,
        "page": null
      }
    ]
  }
  ```

### Streaming Chat
`POST /chat/stream`
- **Body**: Same as synchronous chat
- **Response**: Server-Sent Events (SSE) `text/event-stream` returning raw token strings.

### Get Chat History
`GET /chat/{session_id}/history`
- **Response**: `200 OK`
  ```json
  {
    "session_id": "uuid",
    "history": [
      {"role": "user", "content": "..."},
      {"role": "assistant", "content": "..."}
    ]
  }
  ```

### Delete Chat Session
`DELETE /chat/{session_id}`
- **Response**: `200 OK`

---

## Feedback API (`/feedback`)

### Submit Feedback
`POST /feedback`
- **Body**:
  ```json
  {
    "session_id": "uuid",
    "score": 4,
    "comment": "Good answer"
  }
  ```

### List Feedback
`GET /feedback`
- **Response**: List of feedback records.

---

## Analytics API (`/analytics`)

### Get Metrics
`GET /analytics/metrics`
- **Response**: `200 OK`
  ```json
  {
    "total_documents": 10,
    "documents_by_type": {"resume": 8, "job_description": 2},
    "documents_by_status": {"COMPLETED": 10},
    "average_feedback_score": 4.5,
    "average_faithfulness": 0.95,
    "average_relevancy": 0.92,
    "avg_retrieval_latency_ms": 150
  }
  ```

---

## Health API (`/health`)

### Root Health
`GET /health`
Returns `{"status": "ok", "service": "CogniHire API"}`

### Component Health
- `GET /health/database`
- `GET /health/vectorstore`
- `GET /health/llm`
- `GET /health/disk`
- `GET /health/evaluation`

All return JSON mapping component name to status "ok" or "error".

---

> **Next**: [Database Reference](13_DATABASE_REFERENCE.md)
