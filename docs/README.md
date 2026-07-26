# CogniHire Documentation

> Complete Developer Handbook — Version 1.0

This directory contains the complete technical documentation for the CogniHire hiring-intelligence platform. Every document is grounded in the actual source code and verified against the repository.

## Documentation Index

| # | Document | Description |
|---|----------|-------------|
| 01 | [Project Overview](01_PROJECT_OVERVIEW.md) | Business problem, system purpose, and high-level architecture |
| 02 | [Feature Catalogue](02_FEATURE_CATALOGUE.md) | Every implemented feature with status and details |
| 03 | [Architecture](03_ARCHITECTURE.md) | Clean Architecture layers, dependency rules, and diagrams |
| 04 | [Codebase Guide](04_CODEBASE_GUIDE.md) | Directory-by-directory and file-by-file navigation |
| 05 | [Domain Models](05_DOMAIN_MODELS.md) | All entities, value objects, enums, and their relationships |
| 06 | [Ingestion Pipeline](06_INGESTION_PIPELINE.md) | Upload → Parse → Classify → Chunk → Embed → Index |
| 07 | [Classification & Parsing](07_CLASSIFICATION_AND_PARSING.md) | Rule-based classification, section detection, metadata |
| 08 | [Chunking & Embeddings](08_CHUNKING_AND_EMBEDDINGS.md) | Section-aware chunking and Gemini embedding |
| 09 | [Retrieval Pipeline](09_RETRIEVAL_PIPELINE.md) | Vector, BM25, RRF, and reranking stages |
| 10 | [RAG & Chat Pipeline](10_RAG_AND_CHAT_PIPELINE.md) | Query rewriting, context building, streaming, citations |
| 11 | [Hiring Intelligence](11_HIRING_INTELLIGENCE.md) | Match score, skills, ATS, experience, interviews, summaries |
| 12 | [API Reference](12_API_REFERENCE.md) | Every FastAPI endpoint with schemas and examples |
| 13 | [Database Reference](13_DATABASE_REFERENCE.md) | SQLAlchemy models, tables, ER diagram |
| 14 | [Frontend Guide](14_FRONTEND_GUIDE.md) | Streamlit pages, components, services, session state |
| 15 | [Configuration Reference](15_CONFIGURATION_REFERENCE.md) | All environment variables and settings |
| 16 | [Prompt Management](16_PROMPT_MANAGEMENT.md) | Prompt catalogue, versioning, and variable substitution |
| 17 | [Observability & Evaluation](17_OBSERVABILITY_AND_EVALUATION.md) | LangSmith, RAGAS, logging, analytics |
| 18 | [Security & Error Handling](18_SECURITY_AND_ERROR_HANDLING.md) | Validation, error catalogue, and security controls |
| 19 | [Local Setup](19_LOCAL_SETUP.md) | Step-by-step installation and first-run guide |
| 20 | [Testing Guide](20_TESTING_GUIDE.md) | Test structure, commands, coverage, mocking |
| 21 | [SonarQube Guide](21_SONARQUBE_GUIDE.md) | Local quality analysis workflow |
| 22 | [Performance Guide](22_PERFORMANCE_GUIDE.md) | Resource usage, model loading, optimization |
| 23 | [Troubleshooting](23_TROUBLESHOOTING.md) | Common issues with symptoms, causes, and fixes |
| 24 | [Development Guide](24_DEVELOPMENT_GUIDE.md) | How to safely extend the system |
| 25 | [Glossary](25_GLOSSARY.md) | RAG, embedding, BM25, and other key terms |
| 26 | [Known Limitations](26_KNOWN_LIMITATIONS.md) | Honest assessment of current constraints |

### Diagrams

| Diagram | Description |
|---------|-------------|
| [Architecture Diagrams](diagrams/architecture.md) | Clean Architecture and component diagrams |
| [Ingestion Sequence](diagrams/ingestion-sequence.md) | Document upload and processing flow |
| [RAG Sequence](diagrams/rag-sequence.md) | Chat and analysis retrieval flow |
| [Database ER](diagrams/database-er.md) | Entity-relationship diagram |
| [Multi-Document Isolation](diagrams/multi-document-isolation.md) | Document selection and filtering |

---

## How to Use This Documentation

- **New developers**: Start with [Project Overview](01_PROJECT_OVERVIEW.md) → [Architecture](03_ARCHITECTURE.md) → [Local Setup](19_LOCAL_SETUP.md)
- **Code reviewers**: Use [Codebase Guide](04_CODEBASE_GUIDE.md) and [Architecture](03_ARCHITECTURE.md)
- **Debugging**: Go to [Troubleshooting](23_TROUBLESHOOTING.md) or [Security & Error Handling](18_SECURITY_AND_ERROR_HANDLING.md)
- **Extending the system**: Read [Development Guide](24_DEVELOPMENT_GUIDE.md) and [Architecture](03_ARCHITECTURE.md)
- **Interview preparation**: Review [Project Overview](01_PROJECT_OVERVIEW.md), [Feature Catalogue](02_FEATURE_CATALOGUE.md), and [Architecture](03_ARCHITECTURE.md)
