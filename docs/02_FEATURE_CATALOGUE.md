# 02 — Feature Catalogue

Every feature listed here has been verified against the actual source code. Features marked **⚠️ Not Implemented** are planned but not present in the current codebase.

---

## Document Features

### PDF Upload
| Attribute | Detail |
|-----------|--------|
| **Business Purpose** | Allow recruiters to upload candidate resumes and JDs in PDF format |
| **User** | Recruiter |
| **Frontend Page** | `frontend/pages/01_upload.py` |
| **Backend Endpoint** | `POST /api/v1/documents/upload` |
| **Use Case** | `IngestDocumentUseCase` |
| **Interfaces** | `IDocumentParser` → `PDFDocumentParser` |
| **Database** | `DocumentModel`, `DocumentProcessingJobModel` created |
| **ChromaDB** | Chunks indexed in `documents` collection after processing |
| **Gemini** | Not involved in upload; used for embedding via `BGEEmbeddingProvider` |
| **Input** | PDF file (multipart/form-data), optional `document_type` override |
| **Output** | `{ document_id, status: "processing" }` |
| **Validation** | Extension check (`.pdf`), magic-byte check (`%PDF`), file size ≤ `MAX_UPLOAD_SIZE_MB` (default 10 MB) |
| **Error Cases** | 400 (invalid extension), 400 (invalid magic bytes), 413 (file too large) |
| **Limitations** | No OCR — scanned PDFs with image-only content will produce empty text |

### DOCX Upload
| Attribute | Detail |
|-----------|--------|
| **Business Purpose** | Allow uploading Word documents |
| **Backend Endpoint** | Same as PDF: `POST /api/v1/documents/upload` |
| **Interfaces** | `IDocumentParser` → `DOCXDocumentParser` |
| **Validation** | Extension check (`.docx`, `.doc`), magic-byte check (`PK` — ZIP header) |
| **Limitations** | Complex table layouts may not be parsed correctly; images ignored |

### Multi-File Upload
| Attribute | Detail |
|-----------|--------|
| **Status** | ✅ Implemented |
| **Detail** | Streamlit `file_uploader` accepts `accept_multiple_files=True`. Each file is uploaded individually to the backend via separate POST requests. Per-file classification overrides supported. |

### Resume Classification
| Attribute | Detail |
|-----------|--------|
| **Business Purpose** | Automatically determine if a document is a resume |
| **Implementation** | `RuleBasedDocumentClassifier.classify()` |
| **Method** | Weighted keyword matching with strong resume indicators (score +2.0 each) |
| **Indicators** | `professional summary`, `career objective`, `work experience`, `employment history`, `projects`, `certifications`, `contact details`, `date ranges`, `achievement` |
| **Additional** | Email address pattern adds +1.0 to resume score |
| **Output** | `ClassificationResult` with `document_type`, `confidence`, `resume_score`, `job_description_score`, `matched_indicators` |

### Job Description Classification
| Attribute | Detail |
|-----------|--------|
| **Strong Indicators** | `job description`, `about the role`, `responsibilities`, `required qualifications`, `minimum qualifications`, `preferred qualifications`, `what you will do`, `what we are looking for`, `benefits`, `equal opportunity employer`, `apply now`, `reports to`, `employment type`, `salary range` |
| **Score Weight** | +2.0 per matched strong indicator |

### UNKNOWN Classification
| Attribute | Detail |
|-----------|--------|
| **Trigger** | Either: maximum score < `confidence_threshold` (2.0) OR score margin < `margin_threshold` (1.0) |
| **Behavior** | Document is parsed but **not indexed** into ChromaDB. Processing status is `COMPLETED` but `indexed` is `False`. |
| **User Action** | Manual classification required on the Upload page |

### Manual Document-Type Selection
| Attribute | Detail |
|-----------|--------|
| **Frontend** | Upload page provides a selectbox per file: `Auto Detect`, `Resume`, `Job Description` |
| **Backend** | `document_type` form field sent with upload. If not `auto`, creates `doc_type_override` on the domain `Document` |
| **Effect** | Overrides classifier result; bypasses auto-classification |

### Classification Confidence
| Attribute | Detail |
|-----------|--------|
| **Calculation** | `abs(resume_score - jd_score)` |
| **Storage** | `DocumentModel.classification_confidence` column |
| **Display** | Shown on Upload page next to each processed file |

### Document Reclassification
| Attribute | Detail |
|-----------|--------|
| **Frontend** | Upload page shows UNKNOWN documents with a type selector and "Save & Index" button |
| **Backend Endpoint** | `POST /api/v1/documents/{doc_id}/reclassify` |
| **Process** | Deletes existing vectors → resets job status → re-reads file from `uploads/` → re-runs ingestion with override |
| **Validation** | Document must exist; original file must exist in `uploads/` directory |

### Processing Status Tracking
| Attribute | Detail |
|-----------|--------|
| **Statuses** | `PENDING` → `PROCESSING` → `COMPLETED` or `FAILED` |
| **Backend Endpoint** | `GET /api/v1/documents/{doc_id}/status` |
| **Frontend** | Polls every 2 seconds up to 30 times (60 seconds max) |

### Document Listing
| Attribute | Detail |
|-----------|--------|
| **Backend Endpoint** | `GET /api/v1/documents` |
| **Response** | `DocumentListResponse` with list of `DocumentItemDTO` |
| **Frontend** | Documents page shows table with ID, filename, type, status, chunks, date |

### Document Deletion
| Attribute | Detail |
|-----------|--------|
| **Backend Endpoint** | `DELETE /api/v1/documents/{doc_id}` |
| **Effect** | Deletes `DocumentModel`, `DocumentProcessingJobModel`, and vectors from ChromaDB (`resumes` and `job_descriptions` collections) |
| **Note** | Also attempts deletion from legacy collection names; does not delete file from `uploads/` |

### Document Re-indexing
| Attribute | Detail |
|-----------|--------|
| **Frontend Service** | `DocumentService.reindex_document(doc_id)` calls `POST /documents/{doc_id}/reindex` |
| **Backend Endpoint** | ⚠️ **Not Implemented** — No `/reindex` endpoint exists in the API routers. The frontend service method exists but would return a 404 error. |

---

## RAG Features

### Semantic Retrieval
| Attribute | Detail |
|-----------|--------|
| **Implementation** | `VectorRetriever` |
| **Process** | Embeds query via `IEmbedder.embed_query()` → searches ChromaDB via `IIndexRepository.search()` |
| **Score** | ChromaDB distance score (lower = more similar) |

### BM25 Retrieval
| Attribute | Detail |
|-----------|--------|
| **Implementation** | `BM25Retriever` |
| **Process** | Fetches all chunks matching filters → builds BM25Plus index → scores query against corpus |
| **Tokenization** | Simple whitespace split, lowercased |
| **Filtering** | Chunks with no query token overlap get score 0.0 and are excluded |

### Hybrid Retrieval
| Attribute | Detail |
|-----------|--------|
| **Implementation** | `HybridRetriever` |
| **Process** | Runs vector and BM25 in sequence, interleaves results, deduplicates by chunk ID |
| **Status** | ✅ Implemented but **not used** in production — `RRFRetriever` is used instead in dependency injection |

### Reciprocal Rank Fusion (RRF)
| Attribute | Detail |
|-----------|--------|
| **Implementation** | `RRFRetriever` (the active retriever in production DI) |
| **Formula** | `score = Σ 1/(k + rank + 1)` where `k=60` (configurable) |
| **Process** | Fetches `top_k * 2` (minimum 20) from both vector and BM25 → fuses ranks → sorts by RRF score |
| **Advantage** | Combines semantic and lexical signals without directly comparing incompatible raw scores |

### Cross-Encoder Reranking
| Attribute | Detail |
|-----------|--------|
| **Implementation** | `BGEReranker` |
| **Status** | ⚠️ **Pass-through only** — Returns first `top_k` chunks unchanged. Cross-encoder model was disabled due to corporate firewall blocking HuggingFace downloads. The interface is implemented and wired into DI for future activation. |

### Query Rewriting
| Attribute | Detail |
|-----------|--------|
| **Implementation** | `QueryRewriter` |
| **Trigger** | Only when chat history exists (non-empty `session.history`) |
| **Process** | Sends last 5 messages + follow-up question to Gemini with `query_rewriter` prompt |
| **Fallback** | Returns original query if no history |
| **Prompt** | `query_rewriter` from `prompts.json` |

### Context Construction
| Attribute | Detail |
|-----------|--------|
| **Implementation** | `ContextBuilder.build_context()` |
| **Output** | Formatted context string with `Source: [citation_format]` headers + `Citation` objects |
| **Format** | `[Document_Type | Section_Type | Page X | Chunk Y]` |
| **Separator** | Chunks separated by `\n---\n` |

### Citation Generation
| Attribute | Detail |
|-----------|--------|
| **Model** | `Citation` (domain: `backend/core/domain/chat.py`) |
| **Fields** | `document_id`, `document_type`, `section_type`, `chunk_index`, `page` |
| **Format** | `[Resume | Experience | Page 2 | Chunk 6]` |
| **Attached to** | Chat responses, match scores, missing skills, ATS analysis, interview questions, summaries |

### Multi-Turn Chat
| Attribute | Detail |
|-----------|--------|
| **Implementation** | `ChatPipelineUseCase` with `MemoryChatSessionRepository` |
| **Session Management** | In-memory dictionary; sessions lost on server restart |
| **History** | Full message history maintained in `ChatSession.history` |

### SSE Streaming
| Attribute | Detail |
|-----------|--------|
| **Backend Endpoint** | `POST /api/v1/chat/stream` |
| **Implementation** | `ChatPipelineUseCase.execute_stream()` yields tokens via `GeminiProvider.stream()` |
| **Response** | `StreamingResponse` with `media_type="text/event-stream"` |
| **Frontend** | Displays tokens progressively with cursor indicator `▌` |
| **Limitation** | Session ID and citations are not returned in the stream; frontend saves text only |

### Session History
| Attribute | Detail |
|-----------|--------|
| **Backend Endpoint** | `GET /api/v1/chat/{session_id}/history` |
| **Storage** | In-memory (not persisted to database) |

### Empty-Context Handling
| Attribute | Detail |
|-----------|--------|
| **Behavior** | If retrieval returns no chunks, an empty context string is passed to Gemini. The `chat_generation` prompt instructs: "If the answer is not in the context, state that you don't know." |

---

## Hiring Intelligence Features

### Resume–JD Match Score
| Attribute | Detail |
|-----------|--------|
| **Backend Endpoint** | `POST /api/v1/analyze/match` |
| **Service** | `MatchScoreService` |
| **Weights** | Skills: 40%, Experience: 30%, Education: 15%, Keywords: 15% |
| **Output** | `MatchScoreResponse` with `overall_score`, per-dimension scores, explanations, citations |
| **Gemini** | Generates all scores and explanations via `match_score` prompt |
| **Note** | Scores are entirely Gemini-generated; the prompt instructs weighted calculation |

### Skills Comparison / Missing Skills Analysis
| Attribute | Detail |
|-----------|--------|
| **Backend Endpoint** | `POST /api/v1/analyze/skills` |
| **Service** | `MissingSkillsService` |
| **Output** | `MissingSkillsResponse` with list of `SkillGap` (skill, impact, recommendation) |

### ATS Keyword Analysis
| Attribute | Detail |
|-----------|--------|
| **Backend Endpoint** | `POST /api/v1/analyze/ats` |
| **Service** | `ATSAnalysisService` |
| **Output** | `ATSAnalysisResponse` with `required_keywords`, `present_keywords`, `missing_keywords`, `recommendations` |

### Relevant Experience Analysis
| Attribute | Detail |
|-----------|--------|
| **Backend Endpoint** | ⚠️ **Not Implemented** — No `/analyze/experience` or similar endpoint exists. The `RelevantExperienceService` class exists and is wired in DI, but no API router exposes it. |
| **Service** | `RelevantExperienceService` (exists in codebase) |
| **Use Case Method** | `HiringAnalysisUseCase.generate_relevant_experience()` exists |

### Interview Question Generation
| Attribute | Detail |
|-----------|--------|
| **Backend Endpoint** | `POST /api/v1/analyze/interview-questions` |
| **Service** | `InterviewQuestionService` |
| **Output** | `InterviewQuestionResponse` with `technical_questions`, `behavioral_questions`, `project_questions` |

### Resume Summarization
| Attribute | Detail |
|-----------|--------|
| **Backend Endpoint** | `POST /api/v1/analyze/summary` (with `resume_id`, optional `jd_id`) |
| **Service** | `ResumeSummaryService` |
| **Output** | `SummaryResponse` with `summary` and `key_points` |

### JD Summarization
| Attribute | Detail |
|-----------|--------|
| **Backend Endpoint** | Same as above; returned when `jd_id` is provided |
| **Service** | `JDSummaryService` |

---

## Platform Features

### Feedback Collection
| Attribute | Detail |
|-----------|--------|
| **Backend Endpoint** | `POST /api/v1/feedback` (submit), `GET /api/v1/feedback` (list) |
| **Frontend** | `feedback_widget.py` in chat page — 1–5 star rating per assistant message |
| **Storage** | `FeedbackRecord` table via SQLAlchemy |
| **Validation** | Score must be 1–5 |

### Analytics
| Attribute | Detail |
|-----------|--------|
| **Backend Endpoint** | `GET /api/v1/analytics/metrics` |
| **Metrics** | Average feedback score, average faithfulness, average answer relevancy, recent retrieval latency |
| **Frontend** | Analytics page with Plotly pie chart (document types) and bar chart (status counts) |

### LangSmith Tracing
| Attribute | Detail |
|-----------|--------|
| **Configuration** | `LANGCHAIN_TRACING_V2`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT` in settings |
| **Initialization** | `ObservabilityService.setup()` called on import in `main.py` |
| **Behavior** | Sets environment variables for LangChain's automatic tracing |

### RAGAS Evaluation
| Attribute | Detail |
|-----------|--------|
| **Implementation** | `EvaluationService` |
| **Status** | ⚠️ **Mocked** — Returns hardcoded scores (faithfulness: 0.95, relevancy: 0.92, precision: 0.88, recall: 0.90). Real RAGAS evaluation requires OpenAI keys and is not active. |
| **Trigger** | Background task after each chat response |
| **Storage** | Intended to save to `EvaluationResult` table, but `db_session` is not injected in the API handler |

### Prompt Management
| Attribute | Detail |
|-----------|--------|
| **Implementation** | `PromptManager` — loads from `backend/prompts/prompts.json` |
| **Features** | Version tracking, variable substitution via `.format(**kwargs)` |
| **Prompts** | 8 prompt templates (see [Prompt Management](16_PROMPT_MANAGEMENT.md)) |

### Caching
| Attribute | Detail |
|-----------|--------|
| **Implementation** | `CacheService` — in-memory dictionary with TTL |
| **Used by** | `ChatPipelineUseCase` caches retrieval results for 5 minutes |
| **Key** | `retrieve_{rewritten_query}_{collection_name}` |
| **Limitation** | Not shared across processes; lost on restart |

### Structured Logging
| Attribute | Detail |
|-----------|--------|
| **Implementation** | `LoggingService` with `JSONFormatter` |
| **Output** | JSON to stdout: `{ timestamp, name, level, message }` |
| **Level** | DEBUG in development, INFO otherwise |

### Health Monitoring
| Attribute | Detail |
|-----------|--------|
| **Endpoints** | `/health`, `/health/database`, `/health/vectorstore`, `/health/llm`, `/health/disk`, `/health/evaluation` |
| **LLM Check** | Sends "Ping" to Gemini and checks for "Pong" response |

### Input Validation
| Attribute | Detail |
|-----------|--------|
| **File Validation** | Extension whitelist, magic-byte check, size limit |
| **Analysis Validation** | `validate_analysis_docs` dependency checks document existence, type correctness, processing completion, and indexing status |
| **Feedback Validation** | Score range 1–5 |

---

> **Next**: [Architecture](03_ARCHITECTURE.md)
