# 26 — Known Limitations

The current version of CogniHire (V1.0) is a functional MVP. It has several technical and architectural limitations that must be addressed before moving to a production environment.

## 1. Security & Isolation

### Lack of Multi-Tenancy
All users share a single global ChromaDB index.
- **Risk**: A user can theoretically query or retrieve chunks from a document uploaded by a different company or recruiter if they know the document ID.
- **Future Fix**: Implement user authentication. Add a `tenant_id` column to SQL models and inject it into ChromaDB metadata for hard filtering on all retrievals.

### No API Authentication
The FastAPI backend endpoints (`/api/v1/*`) are entirely open.
- **Risk**: Anyone with network access can upload documents, consume LLM tokens, or delete data.
- **Future Fix**: Implement OAuth2 (JWT) or API Key authentication on all routers.

## 2. Infrastructure & Scalability

### In-Memory State
- **Chat Sessions**: `MemoryChatSessionRepository` loses all chat history on server restart.
- **Embeddings Cache**: `BGEEmbeddingProvider` loses its SHA256 cache on server restart.
- **Future Fix**: Move chat sessions to PostgreSQL and cache to Redis.

### Synchronous BM25 Re-indexing
The `BM25Retriever` fetches all documents from ChromaDB and rebuilds the lexical index on every query.
- **Risk**: As the document corpus grows beyond a few thousand chunks, query latency will become unacceptable (seconds instead of milliseconds).
- **Future Fix**: Replace the local Python `rank_bm25` implementation with a persistent search engine like Elasticsearch or OpenSearch.

### Background Task Constraints
FastAPI `BackgroundTasks` run in the same event loop as the web server.
- **Risk**: If the server crashes or restarts, any pending/processing background tasks are lost forever. They cannot be retried.
- **Future Fix**: Move document ingestion to a distributed task queue like Celery (backed by Redis or RabbitMQ).

## 3. Parsing & Extraction

### Fragile Metadata Extraction
`MetadataExtractor` relies on brittle heuristics:
- Candidate Name is assumed to be the *very first line* of the document. If a resume starts with a header image or "Resume of", the extraction fails.
- Education Level stops at the first match (e.g., matching "B.S." and ignoring a later "Ph.D.").
- **Future Fix**: Use the LLM (via a small specialized prompt) to perform structured entity extraction during ingestion instead of regex.

### No OCR Support
The PyMuPDF parser extracts text layers only. Scanned images (e.g., printed and re-scanned resumes) will yield 0 extracted chunks.
- **Future Fix**: Integrate Tesseract or AWS Textract in the parsing pipeline.

### Table Extraction
Tables in DOCX and PDF files are flattened into linear text, often destroying the semantic relationship between columns (e.g., a table mapping Skills to Years of Experience becomes garbled text).

## 4. API & Feature Deviations

### Relevant Experience Endpoint
The `RelevantExperienceService` and its use case exist and are tested, but **no FastAPI router exposes this endpoint**. It cannot be accessed by the frontend.

### Reindex Endpoint
The frontend `DocumentService` has a `.reindex_document()` method, but the backend lacks a matching `POST /documents/{doc_id}/reindex` endpoint (only `/reclassify` exists).

### Incomplete Deletion
When `DELETE /documents/{doc_id}` is called:
- Vectors are deleted from legacy `"resumes"` and `"job_descriptions"` ChromaDB collections.
- **Bug**: They are *not* deleted from the active `"documents"` collection.
- The physical uploaded file in `uploads/` is not deleted, leading to storage bloat.

## 5. Evaluation

### Mocked RAGAS
The `EvaluationService` returns hardcoded scores (0.95, 0.92, etc.) because real RAGAS execution requires a fast, cheap "evaluator" LLM (like GPT-3.5 or GPT-4o-mini).
- **Future Fix**: Configure a secondary LLM provider specifically for evaluation and implement the actual RAGAS metric calculations.

### Disconnected Database Session
The background task that runs the evaluation does not have access to a database session, so the `EvaluationResult` objects are never actually saved to the database. (They are currently commented out in the `chat.py` background task).

## 6. Model Limitations

### Firewall Workaround (BGE vs. Gemini)
The system was designed for local, open-source models (HuggingFace `bge-large-en` for embeddings and `bge-reranker-base` for reranking). Due to corporate firewall blocks, the system falls back to using Gemini for embeddings, and the reranker is a dummy pass-through.
- **Risk**: Generating embeddings via API is slower and costs money compared to local execution. The lack of a true cross-encoder reranker reduces retrieval precision.

---

> **Return to**: [Project Overview](01_PROJECT_OVERVIEW.md)
