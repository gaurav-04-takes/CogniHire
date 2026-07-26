# 04 — Codebase Guide

## Repository Root

```
CogniHire/
├── backend/                    # Python backend (FastAPI + business logic)
│   ├── main.py                 # FastAPI application entry point
│   ├── api/                    # HTTP routers (API layer)
│   ├── application/            # Use cases, services, DTOs (Application layer)
│   ├── core/                   # Domain models, interfaces, services (Core layer)
│   ├── infrastructure/         # Concrete implementations (Infrastructure layer)
│   ├── dependencies/           # Dependency injection composition root
│   ├── config/                 # Pydantic settings
│   ├── prompts/                # Prompt templates (JSON)
│   └── tests/                  # All test files
├── frontend/                   # Streamlit frontend
│   ├── app.py                  # Streamlit entry point
│   ├── pages/                  # Multipage app pages
│   ├── services/               # API client and service wrappers
│   ├── components/             # Reusable UI components
│   └── state/                  # Session state manager
├── docs/                       # Documentation (you are here)
├── uploads/                    # Persisted uploaded files (runtime, gitignored)
├── chroma_db/                  # ChromaDB persistent storage (runtime, gitignored)
├── .env.example                # Environment variable template
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Test/development dependencies
├── pytest.ini                  # Pytest configuration
├── .coveragerc                 # Coverage configuration
├── sonar-project.properties    # SonarQube project settings
└── README.md                   # Project landing page
```

---

## Backend: API Layer (`backend/api/`)

### `router.py`
- **Purpose**: Central API router that includes all sub-routers
- **Registers**: documents, chat, health, feedback, analytics, analyze routers
- **Also defines**: Root `GET /health` health check

### `documents.py` (283 lines)
- **Purpose**: Document CRUD and lifecycle management
- **Endpoints**: `POST /upload`, `GET /documents`, `GET /{doc_id}`, `GET /{doc_id}/status`, `DELETE /{doc_id}`, `POST /{doc_id}/reclassify`
- **Key classes**: `DocumentItemDTO`, `DocumentListResponse`, `ReclassifyRequest`
- **Key function**: `process_document_background()` — runs ingestion pipeline in FastAPI BackgroundTask
- **Dependencies**: `IngestDocumentUseCase`, `IIndexRepository`, SQLAlchemy session
- **Side effects**: Creates database records, saves files to `uploads/`, triggers background processing

### `analyze.py` (115 lines)
- **Purpose**: Hiring intelligence analysis endpoints
- **Endpoints**: `POST /match`, `POST /skills`, `POST /ats`, `POST /interview-questions`, `POST /summary`
- **Key class**: `AnalysisRequest` (resume_id, optional jd_id)
- **Key function**: `validate_analysis_docs()` — validates document existence, type, processing status, and indexing
- **Dependencies**: `HiringAnalysisUseCase`
- **Note**: No `/experience` endpoint despite the service existing

### `chat.py` (86 lines)
- **Purpose**: Chat and streaming endpoints
- **Endpoints**: `POST /chat`, `POST /chat/stream`, `GET /chat/{session_id}/history`, `DELETE /chat/{session_id}`
- **Key classes**: `ChatRequest`, `ChatResponse`
- **Side effects**: Triggers background RAGAS evaluation after each chat response

### `health.py` (85 lines)
- **Purpose**: System health check endpoints
- **Endpoints**: `GET /health/database`, `GET /health/vectorstore`, `GET /health/llm`, `GET /health/disk`, `GET /health/evaluation`
- **LLM check**: Sends "Ping" to Gemini, expects "Pong"

### `feedback.py` (50 lines)
- **Purpose**: User feedback collection
- **Endpoints**: `POST /feedback`, `GET /feedback`
- **Validation**: Score 1–5

### `analytics.py` (28 lines)
- **Purpose**: System metrics aggregation
- **Endpoint**: `GET /analytics/metrics`
- **Metrics**: Average feedback, faithfulness, relevancy, retrieval latency

### `upload.py` (136 lines)
- **Purpose**: Legacy upload router (superseded by `documents.py`)
- **Note**: Contains duplicate upload and status endpoints. Both are registered, but `documents.py` is the primary router.

---

## Backend: Application Layer (`backend/application/`)

### Use Cases (`application/use_cases/`)

#### `ingest_document.py`
- **Class**: `IngestDocumentUseCase`
- **Method**: `execute(document) → (chunk_count, doc_type, classification_result)`
- **Pipeline**: Parse → Classify → (Override?) → Extract Metadata → Detect Sections → Chunk → Embed → Index
- **UNKNOWN handling**: Returns 0 chunks, does not index

#### `chat_pipeline.py`
- **Class**: `ChatPipelineUseCase`
- **Methods**: `execute()` (full response), `execute_stream()` (token-by-token)
- **Pipeline**: Session management → Query rewrite → Retrieve (with cache) → Rerank → Build context → Generate → Attach citations → Save session

#### `hiring_analysis_pipeline.py`
- **Class**: `HiringAnalysisUseCase`
- **Methods**: `generate_match_score()`, `generate_missing_skills()`, `generate_ats_analysis()`, `generate_relevant_experience()`, `generate_interview_questions()`, `generate_resume_summary()`, `generate_jd_summary()`
- **Key helper**: `_get_document_context()` — retrieves chunks for a specific document_id + doc_type using `$and` filter

#### `retrieve_chunks.py`
- **Class**: `RetrieveRelevantChunksUseCase`
- **Purpose**: Standalone retrieval (not currently used by any API endpoint)

### Services (`application/services/`)

#### `query_rewriter.py`
- **Class**: `QueryRewriter`
- **Method**: `rewrite(query, history) → str`
- **Behavior**: Skips rewriting if no history; uses last 5 messages

#### `context_builder.py`
- **Class**: `ContextBuilder`
- **Method**: `build_context(chunks) → (context_str, citations)`
- **Output format**: `Source: [citation]\nContent:\n{text}\n`

### Analysis Services (`application/services/analysis/`)

All analysis services follow the same pattern:
1. Extend `BaseAnalysisService` (provides `_parse_json()` for LLM response parsing)
2. Accept `ILLMProvider` and `PromptManager` in constructor
3. Have an `analyze()` method that retrieves a prompt, sends JD + Resume context to Gemini, parses JSON response
4. Attach formatted citations to the result

| Service | Prompt Key | Response Model |
|---------|-----------|----------------|
| `MatchScoreService` | `match_score` | `MatchScoreResponse` |
| `MissingSkillsService` | `missing_skills` | `MissingSkillsResponse` |
| `ATSAnalysisService` | `ats_analysis` | `ATSAnalysisResponse` |
| `RelevantExperienceService` | `relevant_experience` | `RelevantExperienceResponse` |
| `InterviewQuestionService` | `interview_questions` | `InterviewQuestionResponse` |
| `ResumeSummaryService` | `summary_resume` | `SummaryResponse` |
| `JDSummaryService` | `summary_jd` | `SummaryResponse` |

### DTOs (`application/dto/`)

#### `retrieval.py`
- `RetrieveRequest`: query, filters, top_k, collection_name
- `RetrievedChunk`: chunk_id, document_id, document_type, section_type, chunk_index, score, text
- `RetrieveResponse`: query, results

---

## Backend: Core Layer (`backend/core/`)

### Domain Models (`core/domain/`)

See [Domain Models](05_DOMAIN_MODELS.md) for complete documentation.

### Interfaces (`core/interfaces/`)

See [Interface Mapping](03_ARCHITECTURE.md#layer-responsibilities) and individual interface documentation.

### Services (`core/services/`)

| File | Class | Purpose |
|------|-------|---------|
| `prompt_manager.py` | `PromptManager` | Loads prompts from JSON, supports variable substitution and versioning |
| `cache_service.py` | `CacheService` | In-memory cache with TTL; singleton `cache_service` instance |
| `evaluation_service.py` | `EvaluationService` | RAGAS evaluation wrapper (mocked in V1) |
| `logging_service.py` | `LoggingService` | JSON-formatted structured logging; singleton `logger` instance |
| `observability_service.py` | `ObservabilityService` | LangSmith tracing setup via environment variables |

---

## Backend: Infrastructure Layer (`backend/infrastructure/`)

### Parsers (`infrastructure/parsers/`)

| File | Class | Interface | Purpose |
|------|-------|-----------|---------|
| `pdf_parser.py` | `PDFDocumentParser` | `IDocumentParser` | Extracts text from PDFs using PyMuPDF |
| `docx_parser.py` | `DOCXDocumentParser` | `IDocumentParser` | Extracts text from DOCX using python-docx |
| `section_parser.py` | `RuleBasedSectionParser` | `ISectionParser` | Regex-based section detection for resumes and JDs |
| `metadata_extractor.py` | `MetadataExtractor` | (no interface) | Regex-based metadata extraction (years of experience, education, name) |

### Classifiers (`infrastructure/classifiers/`)

| File | Class | Interface |
|------|-------|-----------|
| `rule_based_classifier.py` | `RuleBasedDocumentClassifier` | `IDocumentClassifier` |

### Chunkers (`infrastructure/chunkers/`)

| File | Class | Interface |
|------|-------|-----------|
| `section_chunker.py` | `SectionAwareChunker` | (no interface) |

### Embedders (`infrastructure/embedders/`)

| File | Class | Interface |
|------|-------|-----------|
| `bge_embedder.py` | `BGEEmbeddingProvider` | `IEmbedder` |

> **Note**: Despite the class name `BGEEmbeddingProvider`, this class actually uses Google Gemini embeddings (`models/gemini-embedding-2`) via `GoogleGenerativeAIEmbeddings`. The "BGE" name is historical — the original plan used HuggingFace BAAI/bge models, but corporate firewall restrictions required switching to Gemini embeddings.

### Retrievers (`infrastructure/retrievers/`)

| File | Class | Interface | Status |
|------|-------|-----------|--------|
| `vector_retriever.py` | `VectorRetriever` | `IRetriever` | Active |
| `bm25_retriever.py` | `BM25Retriever` | `IRetriever` | Active |
| `rrf_retriever.py` | `RRFRetriever` | `IRetriever` | **Active (production retriever)** |
| `hybrid_retriever.py` | `HybridRetriever` | `IRetriever` | Exists but not wired in DI |

### Rerankers (`infrastructure/rerankers/`)

| File | Class | Interface | Status |
|------|-------|-----------|--------|
| `bge_reranker.py` | `BGEReranker` | `IReranker` | Pass-through (no actual reranking) |

### LLM Providers (`infrastructure/llm/`)

| File | Class | Interface |
|------|-------|-----------|
| `gemini_provider.py` | `GeminiProvider` | `ILLMProvider` |

### Repositories (`infrastructure/repositories/`)

| File | Class | Interface | Storage |
|------|-------|-----------|---------|
| `sqlite_document_repository.py` | `SQLiteDocumentRepository` | `IDocumentRepository` | SQLite (raw SQL) |
| `memory_chat_session_repository.py` | `MemoryChatSessionRepository` | `IChatSessionRepository` | In-memory dict |

> **Note**: `SQLiteDocumentRepository` references `DocumentRecord` and `DocumentStatus` from domain, but these classes are not defined in the current `document.py`. This file appears to be a legacy implementation. The active document management uses SQLAlchemy models directly in the API layer.

### Vector Stores (`infrastructure/vectorstores/`)

| File | Class | Interface |
|------|-------|-----------|
| `chroma_repository.py` | `ChromaIndexRepository` | `IIndexRepository` |

### Database (`infrastructure/database/`)

| File | Purpose |
|------|---------|
| `models.py` | SQLAlchemy ORM models (DocumentModel, DocumentProcessingJobModel, etc.) |
| `session.py` | SQLAlchemy engine and session factory |

---

## Frontend (`frontend/`)

### Pages

| File | Title | Purpose |
|------|-------|---------|
| `app.py` | CogniHire Home | Main entry point, session init, welcome text |
| `pages/01_upload.py` | Document Ingestion | File upload, classification overrides, status polling, UNKNOWN resolution |
| `pages/02_analyze.py` | Analysis Dashboard | Resume/JD selection, run analysis, render results, export |
| `pages/03_chat.py` | Chat | Streaming chat with citation cards and feedback |
| `pages/04_documents.py` | Document Management | List, view, delete documents |
| `pages/05_analytics.py` | Analytics | Metrics, charts, document distribution |

### Services

| File | Class | Purpose |
|------|-------|---------|
| `api_client.py` | `APIClient` | HTTP client wrapping requests; `get`, `post`, `delete`, `stream_post` |
| `document_service.py` | `DocumentService` | Document CRUD operations via API |
| `analysis_service.py` | `AnalysisService` | Analysis API calls |
| `chat_service.py` | `ChatService` | Chat and streaming API calls |
| `export_service.py` | `ExportService` | PDF report generation using fpdf2 |

### Components

| File | Function | Purpose |
|------|----------|---------|
| `citation_card.py` | `citation_card()` | Expandable citation display |
| `feedback_widget.py` | `feedback_widget()` | 1–5 star rating buttons |
| `match_score_widget.py` | `match_score_widget()` | Plotly gauge chart + dimension breakdown |
| `skill_gap_table.py` | `skill_gap_table()` | Missing skills table + ATS keyword columns |

### State

| File | Class | Purpose |
|------|-------|---------|
| `session_manager.py` | `SessionManager` | Initializes and manages `st.session_state` keys |

---

## Configuration Files

| File | Purpose |
|------|---------|
| `.env.example` | Environment variable template (safe to commit) |
| `.env` | Actual secrets (gitignored) |
| `requirements.txt` | Production Python dependencies |
| `requirements-dev.txt` | Test and development dependencies |
| `pytest.ini` | Test runner configuration |
| `.coveragerc` | Code coverage settings (85% threshold) |
| `sonar-project.properties` | SonarQube project configuration |
| `.gitignore` | Git exclusion rules |

---

> **Next**: [Domain Models](05_DOMAIN_MODELS.md)
