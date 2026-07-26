# 22 — Performance Guide

## Document Ingestion

Document processing (parsing, chunking, embedding) is the most CPU-intensive part of the application. 

### Background Processing
All ingestion occurs in a `fastapi.BackgroundTasks` runner. The HTTP response returns immediately (in ~50ms), while processing takes 2-5 seconds depending on document length.

### Caching Embeddings
`BGEEmbeddingProvider` maintains an in-memory SHA256 cache of texts it has already embedded.
- **Benefit**: If the same document (or identical sections across templates) is uploaded multiple times, API calls to Gemini for embeddings are skipped.
- **Drawback**: High memory usage over long uptimes. The cache is lost on process restart.

## Retrieval & Search

### BM25 Re-indexing
The `BM25Retriever` fetches all chunks from ChromaDB and builds a new BM25 index **on every query**.
- **Current state**: Works perfectly for hundreds of documents (latency ~100ms).
- **Bottleneck**: At scale (10,000+ chunks), pulling all texts from ChromaDB into memory on every query will cause severe latency and memory pressure. 
- **Future fix**: The BM25 index must be persisted and updated incrementally (e.g., using Elasticsearch instead of a local Python BM25 implementation).

### Retrieval Caching
`ChatPipelineUseCase` utilizes `CacheService` to cache retrieval results for 5 minutes.
- **Key**: `retrieve_{rewritten_query}_documents`
- **Impact**: Identical follow-up questions within the same chat session skip the retrieval phase entirely.

## LLM Latency

The system relies on Google Gemini for all generative tasks.

| Task | Average Latency | Note |
|------|-----------------|------|
| Streaming Chat | TTFB: ~800ms | Fast time-to-first-byte provides excellent UX. |
| Match Score | 3-5 seconds | Large context (Resume + JD) and complex JSON schema. |
| Interview Prep | 4-6 seconds | Generating detailed technical questions is slow. |

### SSE (Server-Sent Events)
Streaming chat uses SSE to send tokens to the frontend as soon as they are generated. This prevents the user from waiting 5 seconds before seeing any text.

---

> **Next**: [Troubleshooting](23_TROUBLESHOOTING.md)
