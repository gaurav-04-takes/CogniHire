# 15 — Configuration Reference

CogniHire uses `pydantic-settings` to manage configuration. Settings are loaded from the environment, defaulting to the `.env` file in the repository root.

**File**: `backend/config/settings.py`

## Core Application Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `"development"` | Application mode (`development`, `staging`, `production`) |
| `APP_NAME` | `"CogniHire API"` | FastAPI application title |
| `APP_VERSION` | `"1.0.0"` | FastAPI application version |
| `API_V1_STR` | `"/api/v1"` | Global prefix for all API routers |
| `CORS_ORIGINS` | `["*"]` | Allowed CORS origins (comma-separated list in .env) |
| `BACKEND_API_URL` | `"http://localhost:8000/api/v1"` | URL for the Streamlit frontend to hit |

## Storage & Paths

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `"sqlite:///./cognihire.db"` | SQLAlchemy connection string |
| `CHROMA_PERSIST_DIRECTORY` | `"./data/chroma"` | Path where ChromaDB saves vector indexes |
| `UPLOAD_DIRECTORY` | `"./uploads"` | Path where uploaded PDFs/DOCXs are temporarily stored |
| `MAX_UPLOAD_SIZE_MB` | `10` | Maximum file size allowed by the upload endpoint |
| `CACHE_TYPE` | `"memory"` | Type of cache to use (currently only `memory` is implemented) |

## Large Language Model (LLM) Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `"gemini"` | Active LLM implementation (used by DI container) |
| `GEMINI_API_KEY` | `""` | **Required.** Google AI Studio API Key |
| `GEMINI_MODEL` | `"gemini-1.5-pro-latest"` | Default model for text generation |
| `GEMINI_TEMPERATURE` | `0.2` | Generation temperature (low for factual RAG) |
| `GEMINI_MAX_TOKENS` | `4096` | Max output tokens per response |

## Retrieval & Pipeline Parameters

| Variable | Default | Description |
|----------|---------|-------------|
| `RRF_K` | `60` | Reciprocal Rank Fusion smoothing constant |
| `RETRIEVAL_TOP_K` | `10` | Default number of chunks to retrieve for chat |
| `EXPANDED_RETRIEVAL_TOP_K`| `20` | Pre-fusion fetch size for vector/BM25 retrievers |
| `ANALYSIS_CHUNK_LIMIT` | `100` | Safety limit on chunks retrieved for full-document analysis |

## Observability & LangSmith

| Variable | Default | Description |
|----------|---------|-------------|
| `LANGSMITH_TRACING` | `"false"` | Master toggle for LangSmith observability |
| `LANGCHAIN_TRACING_V2` | `"false"` | Required by LangChain to enable tracing |
| `LANGCHAIN_API_KEY` | `""` | LangSmith API Key (if tracing is true) |
| `LANGCHAIN_PROJECT` | `"CogniHire"` | LangSmith Project Name |

## Legacy Machine Learning (BGE/Torch)

These settings exist in `.env.example` but are largely unused since the switch to Gemini embeddings due to firewall constraints.

| Variable | Default | Description |
|----------|---------|-------------|
| `ML_DEVICE` | `"auto"` | CPU/CUDA/MPS for local Torch models |
| `EMBEDDING_BATCH_SIZE` | `8` | Batch size for sentence-transformers |
| `RERANK_BATCH_SIZE` | `4` | Batch size for cross-encoders |
| `TORCH_NUM_THREADS` | `2` | CPU threads for local inference |

---

> **Next**: [Prompt Management](16_PROMPT_MANAGEMENT.md)
