# Error Handling & Validation Report

## 1. Executive Summary
An API-wide audit was conducted to verify standard error responses, exception safety, validation handling, and timeout mitigation across CogniHire's endpoints.

**Status:** Compliant. No raw stack traces are leaked to the client.

## 2. API Endpoint Audit

### 2.1 `/documents/upload`
- **Validation Handling:** FastAPI `UploadFile` constraints are manually extended with strict logic to reject unsupported formats (returning 400 Bad Request).
- **Size Validation:** Returns a standard `413 Payload Too Large` if `len(content) > MAX_UPLOAD_SIZE_MB`.
- **Exception Safety:** The background ingestion task is wrapped in a `try/except/finally`. Database sessions are strictly closed, preventing connection leaks. Failed ingestion updates the `ProcessingStatus` to `FAILED` in the database, allowing the client to safely poll the error state.

### 2.2 `/analyze/*` Endpoints
- **Validation Handling:** If a requested `document_id` does not exist in the ChromaDB vector store, the APIs safely catch the missing chunks and return `404 Not Found`.
- **LLM Timeout/Parsing Errors:** `BaseAnalysisService` utilizes `_parse_json` which gracefully handles cases where the LLM fails to output valid JSON. The endpoints wrap these errors and return a `500 Internal Server Error` with a sanitized message.

### 2.3 `/chat`
- **Validation Handling:** Validates the `session_id`. If omitted, safely generates a new one.
- **Coverage:** ✅ `GeminiProvider` catches and logs `google.api_core.exceptions` (like RateLimit or Quota exceptions) and standardizes them before bubbling them up to the API.
- **Exception Safety:** The entire execution pipeline is wrapped in a high-level `try/except`. Errors (such as the Gemini API being unreachable or API key being invalid) correctly yield a standard 500 error rather than crashing the ASGI server.

## 3. Standardization
All JSON error responses adhere to standard HTTP status codes:
- `400`: Bad Request (Invalid file types, missing parameters)
- `404`: Not Found (Session missing, document not embedded)
- `413`: Payload Too Large (File size limits)
- `500`: Internal Server Error (LLM failure, parsing failure, generic catch-all)
