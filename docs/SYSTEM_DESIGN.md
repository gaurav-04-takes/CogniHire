# System Design

## 1. Document Ingestion Pipeline
1. **Extraction:** PyMuPDF parses `.pdf` files. `python-docx` parses `.docx` files.
2. **Classification:** A rule-based classifier determines if the text is a Resume or a JD based on keyword density (e.g., "Education", "Experience" vs "Requirements", "Responsibilities").
3. **Chunking:** A `SectionAwareChunker` divides the document into semantic blocks preserving headers (e.g., stopping a chunk before a new major header).
4. **Embedding:** `BGEEmbeddingProvider` generates dense vectors.
5. **Storage:** Stored in ChromaDB under `resumes` or `job_descriptions` collections.

## 2. Advanced Retrieval (RAG)
1. **Query Rewriting:** A prompt rewrites conversational chat history into a dense, standalone search query.
2. **Hybrid Search:** Both Vector (Semantic) and BM25 (Lexical) retrievers execute against ChromaDB.
3. **RRF:** The results are merged using Reciprocal Rank Fusion `1 / (k + rank)`.
4. **Reranking:** A Cross-Encoder model re-scores the fused chunks, dropping irrelevant context.
5. **Generation:** Google Gemini generates the final answer strictly grounded in the re-ranked chunks.
