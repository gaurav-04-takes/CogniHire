# Operations Guide

## Deployment Requirements
- **Memory:** Minimum 8GB RAM (VectorDB).
- **Storage:** Minimum 20GB SSD for ChromaDB vectors and SQLite DB.

## Monitoring
CogniHire implements several `/health` endpoints to plug into standard orchestrators (e.g., Kubernetes readiness/liveness probes):
- `/health/database`: Verifies SQLite connection.
- `/health/vectorstore`: Verifies ChromaDB index accessibility.
- `/health/llm`: Pings Google Gemini API to ensure the API Key is valid and the model is responsive.
- `/health/disk`: Asserts sufficient storage for incoming documents.

## Observability
If you set `LANGCHAIN_TRACING_V2=true` and provide a `LANGCHAIN_API_KEY` in your `.env`, all LLM chains are transmitted to LangSmith for real-time observability of token usage, latency, and prompt execution.

## Data Persistence
- Back up `cognihire.db` (SQLite) routinely.
- Back up the ChromaDB directory (defined by `CHROMADB_DIR` in `.env`) to preserve vectors.
