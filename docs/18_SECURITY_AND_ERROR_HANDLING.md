# 18 — Security & Error Handling

## Input Validation & Security

### File Uploads
- **Extension Allowlist**: Only `.pdf`, `.docx`, `.doc` allowed.
- **Magic Byte Validation**: Prevent malicious files masked with valid extensions.
  - PDF must start with `%PDF`
  - DOCX must start with `PK`
- **Size Limits**: Enforced by `MAX_UPLOAD_SIZE_MB` (default 10MB) to prevent DoS via large file processing.
- **Directory Traversal**: Upload filenames are discarded; files are saved using securely generated UUIDs (`uploads/{uuid}.{ext}`).

### API Endpoints
- **Pydantic Validation**: All POST bodies are validated against strict Pydantic schemas (e.g., `ChatRequest`, `AnalysisRequest`).
- **Dependency Checks**: The `validate_analysis_docs` dependency ensures that requested documents actually exist, have the correct document type, and have successfully finished processing before allowing analysis to proceed.

### Security Deficits (Known Limitations)
- **No Authentication**: The API is completely open. Anyone with the URL can upload documents or query the API.
- **No Authorization / Multi-Tenancy**: All users share the same ChromaDB instance and can query any document if they know (or guess) the UUID. There is no concept of "User A's documents."
- **Path Traversal Risk**: While UUIDs are used for document names, robust path sanitization is not explicitly implemented for file reading operations.

## Error Handling

### HTTP Exceptions
FastAPI's `HTTPException` is used to return structured error responses.

| Status Code | Reason | Examples |
|-------------|--------|----------|
| **400 Bad Request** | Client error | Invalid file extension, invalid magic bytes, requesting analysis on a document that is still processing. |
| **404 Not Found** | Resource missing | Document ID not found in database. |
| **413 Payload Too Large**| File limit exceeded| Uploaded file > 10MB. |
| **500 Internal Server Error** | System failure | LLM API timeout, database connection failure. |

### Background Task Errors
Exceptions raised inside the background ingestion pipeline (`process_document_background`) cannot return HTTP responses to the user because the HTTP request has already completed.

Instead, these errors are caught globally within the task:
1. `job.status` is set to `ProcessingStatus.FAILED`.
2. `job.error_message` is populated with `str(e)`.
3. The database session is committed.
4. The user sees the failure when polling the `/status` endpoint.

### LLM Parsing Errors
When the LLM fails to return valid JSON (despite explicit prompting):
1. `BaseAnalysisService._parse_json` attempts to strip markdown code blocks.
2. If `json.loads` fails, it catches `json.JSONDecodeError`.
3. It falls back to returning a default/empty instance of the requested Pydantic model rather than crashing the API.

---

> **Next**: [Local Setup](19_LOCAL_SETUP.md)
