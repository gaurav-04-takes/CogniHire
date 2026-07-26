# 01 — Project Overview

## What Is CogniHire?

CogniHire is an AI-powered **Hiring Intelligence** platform that helps recruiters evaluate candidates by comparing their resumes against job descriptions. Instead of relying on rigid keyword matching like traditional Applicant Tracking Systems (ATS), CogniHire uses **Retrieval-Augmented Generation (RAG)** to understand the semantic meaning of a candidate's experience and qualifications.

## The Business Problem

Recruiters face several challenges:

1. **Volume**: Hundreds of resumes per open position must be reviewed manually.
2. **Keyword Mismatch**: A candidate who writes "React Engineer" may be filtered out by an ATS seeking "Frontend Developer" — despite being perfectly qualified.
3. **Context Loss**: ATS keyword counts ignore the context in which skills appear (e.g., 5 years leading React teams vs. a single React tutorial).
4. **Cross-Document Comparison**: Manually comparing skills, experience, and education across a resume and a JD is time-consuming and error-prone.
5. **No Traceability**: Hiring decisions often lack an auditable trail back to specific resume claims.

## Why RAG?

RAG combines two powerful techniques:

- **Retrieval**: Relevant sections of documents are retrieved using semantic similarity and keyword matching, ensuring the LLM only sees factual, grounded content.
- **Generation**: A Large Language Model (Gemini) generates human-readable analysis, but is constrained to only use retrieved context — reducing hallucination.

## Why Citations?

Every analysis result includes **citations** that trace each claim back to a specific section, chunk, and page of the source document. This enables:

- Auditability of hiring decisions
- Trust in AI-generated recommendations
- Easy verification by human reviewers

## Who Uses CogniHire?

| Role | Usage |
|------|-------|
| **Recruiter** | Upload resumes and JDs, run match analysis, review skill gaps, prepare interview questions |
| **Hiring Manager** | Review AI-generated match scores and experience rankings |
| **HR Admin** | Monitor system analytics and feedback quality |
| **Developer** | Extend the platform, add new analysis features, integrate new LLM providers |

## Implemented Features (V1)

### Document Management
- PDF and DOCX upload with magic-byte validation
- Automatic document classification (resume vs. job description)
- Manual classification override for ambiguous documents
- Document reclassification with re-indexing
- Document deletion with vector store cleanup
- Processing status tracking with polling

### Retrieval-Augmented Generation
- Section-aware document chunking
- Gemini-powered semantic embeddings
- Vector similarity search (ChromaDB)
- BM25 keyword search
- Reciprocal Rank Fusion (RRF) for hybrid retrieval
- Query rewriting for multi-turn conversations
- Context building with citation attachment
- SSE streaming responses

### Hiring Intelligence
- Resume–JD match scoring with weighted dimensions (Skills 40%, Experience 30%, Education 15%, Keywords 15%)
- Missing skills gap analysis
- ATS keyword optimization analysis
- Interview question generation (technical, behavioral, project-based)
- Resume and JD summarization

### Platform
- Feedback collection (1–5 star ratings)
- System analytics dashboard
- LangSmith tracing integration
- RAGAS evaluation (mocked in V1)
- Structured JSON logging
- Health monitoring endpoints
- PDF and JSON report export

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend API | FastAPI (Python) |
| Frontend | Streamlit |
| LLM Provider | Google Gemini (via LangChain) |
| Embeddings | Google Gemini Embedding API (`gemini-embedding-2`) |
| Vector Database | ChromaDB (persistent, local) |
| Relational Database | SQLite (via SQLAlchemy) |
| Document Parsing | PyMuPDF (PDF), python-docx (DOCX) |
| Keyword Retrieval | rank-bm25 (BM25Plus) |
| Observability | LangSmith, structured logging |
| Evaluation | RAGAS (mocked in V1) |
| Visualization | Plotly |
| Report Export | fpdf2 |

## High-Level System Flow

```
User
  → Streamlit Frontend
    → FastAPI Backend
      → Application Use Case
        → Core Interface
          → Infrastructure Implementation
            → Database (SQLite), ChromaDB, or Gemini API
          ← Response with data
        ← Domain objects
      ← DTO / JSON
    ← API Response
  ← Rendered UI with citations
```

## Architecture Summary

CogniHire follows **Clean Architecture** principles:

- **Core Domain**: Pure business entities (Document, Chunk, ChatSession) with no framework dependencies
- **Core Interfaces**: Abstract contracts (IDocumentParser, IRetriever, ILLMProvider) that define what the system needs
- **Application Layer**: Use cases (IngestDocument, ChatPipeline, HiringAnalysis) that orchestrate business logic
- **Infrastructure Layer**: Concrete implementations (PDFParser, GeminiProvider, ChromaDB) that satisfy interfaces
- **API Layer**: FastAPI routers that translate HTTP requests to use case calls
- **Frontend Layer**: Streamlit pages that communicate exclusively through the API

Dependency flows **inward**: Infrastructure depends on Interfaces, never the reverse. This enables swapping providers (e.g., replacing Gemini with another LLM) without touching business logic.

---

> **Next**: [Feature Catalogue](02_FEATURE_CATALOGUE.md) for detailed feature documentation.
