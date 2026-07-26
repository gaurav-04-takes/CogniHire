# 08 — Chunking & Embeddings

## Section-Aware Chunking

**File**: `backend/infrastructure/chunkers/section_chunker.py`  
**Class**: `SectionAwareChunker`  
**No interface**: Used directly by `IngestDocumentUseCase`

### Why Section-Aware?

Traditional chunking splits documents at arbitrary character boundaries. This loses critical context — a chunk might contain half of the "Experience" section and half of the "Education" section, confusing the retriever. Section-aware chunking ensures:

1. **Section boundaries are preserved**: Each chunk belongs to exactly one section
2. **Metadata is accurate**: Each chunk carries its correct `section_type`
3. **Long sections are sub-chunked**: Sections exceeding `chunk_size` are split using `RecursiveCharacterTextSplitter`

### Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `chunk_size` | 1000 | Maximum characters per chunk |
| `chunk_overlap` | 200 | Characters of overlap between sub-chunks within a section |

### Text Splitter

Uses LangChain's `RecursiveCharacterTextSplitter` with separators:
```
["\n\n", "\n", " ", ""]
```

This splits at paragraph boundaries first, then line breaks, then word breaks, and finally character boundaries as a last resort.

### Chunking Algorithm

```python
for each section in parsed_document.sections:
    sub_texts = text_splitter.split_text(section.content)
    for each sub_text in sub_texts:
        create Chunk(
            id = "{document_id}_chunk_{global_index}",
            document_id = doc.document_id,
            doc_type = doc.doc_type,
            section_type = section.title,
            text = sub_text,
            metadata = {
                document_id, document_type, section_type,
                chunk_index, + document-level metadata
            }
        )
        global_index += 1
```

### Metadata Attached to Each Chunk

| Key | Source | Example |
|-----|--------|---------|
| `document_id` | Document UUID | `"abc-123-def"` |
| `document_type` | Classifier result | `"resume"` |
| `section_type` | Section parser | `"Experience"` |
| `chunk_index` | Global counter | `3` |
| `years_of_experience` | MetadataExtractor | `5` |
| `education_level` | MetadataExtractor | `"Master"` |
| `candidate_name` | MetadataExtractor | `"John Doe"` |

### Example

Given a resume with sections:
- Header (50 chars)
- Experience (2500 chars)
- Education (300 chars)
- Skills (150 chars)

With `chunk_size=1000, chunk_overlap=200`:

| Chunk # | Section | Characters | Notes |
|---------|---------|------------|-------|
| 0 | Header | 50 | Short, single chunk |
| 1 | Experience | 1000 | First sub-chunk |
| 2 | Experience | 1000 | Second sub-chunk (200 overlap) |
| 3 | Experience | ~700 | Third sub-chunk (200 overlap) |
| 4 | Education | 300 | Single chunk |
| 5 | Skills | 150 | Single chunk |

Total: 6 chunks, each carrying its section's `section_type` metadata.

---

## Embedding Generation

**File**: `backend/infrastructure/embedders/bge_embedder.py`  
**Class**: `BGEEmbeddingProvider`  
**Interface**: `IEmbedder`

### Naming Note

Despite the class name `BGEEmbeddingProvider`, this implementation uses **Google Gemini embeddings**, not HuggingFace BAAI/bge models. The name is a historical artifact — the original design planned to use local BGE models, but corporate firewall restrictions preventing HuggingFace downloads led to switching to Gemini's cloud embedding API.

### Configuration

| Setting | Value | Source |
|---------|-------|--------|
| Model | `models/gemini-embedding-2` | Hardcoded in DI container |
| API Key | `settings.GEMINI_API_KEY` | `.env` file |
| Batch Size | Not specified | LangChain default |

### Implementation

Uses `GoogleGenerativeAIEmbeddings` from `langchain-google-genai`:

```python
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-2",
    google_api_key=settings.GEMINI_API_KEY
)
```

### Methods

| Method | Purpose | Input | Output |
|--------|---------|-------|--------|
| `embed_documents(texts)` | Embed multiple texts for indexing | `List[str]` | `List[List[float]]` |
| `embed_query(text)` | Embed a single query for retrieval | `str` | `List[float]` |

### Embedding Cache

A SHA256-based in-memory cache (`_embedding_cache`) prevents re-embedding identical text chunks:

```python
cache_key = hashlib.sha256(text.encode()).hexdigest()
if cache_key in self._embedding_cache:
    return cached_embedding
```

**Scope**: Process-level only; lost on restart.

### Embedding Attachment

After embedding, each embedding vector is temporarily stored in `chunk.metadata["embedding"]`. When `ChromaIndexRepository.index_chunks()` processes the chunks, it:

1. Pops `embedding` from metadata
2. Passes embeddings separately to `collection.add(embeddings=...)`

This prevents the large float arrays from being stored as ChromaDB metadata (which has value-type restrictions).

---

## ChromaDB Indexing

**File**: `backend/infrastructure/vectorstores/chroma_repository.py`  
**Class**: `ChromaIndexRepository`  
**Interface**: `IIndexRepository`

### Collection Strategy

| Aspect | Detail |
|--------|--------|
| Active collection | `"documents"` — all document types stored together |
| Legacy collections | `"resumes"`, `"job_descriptions"` — referenced in delete operations for backward compatibility |
| Isolation method | ChromaDB metadata filters on `document_id` and `document_type` |

### Persistence

| Setting | Value |
|---------|-------|
| Directory | `settings.CHROMA_PERSIST_DIRECTORY` (default: `./data/chroma`) |
| Client | `chromadb.PersistentClient` |

### Index Operations

#### `index_chunks(chunks, collection_name)`

```python
for each chunk:
    embedding = chunk.metadata.pop("embedding")  # Remove from metadata
    clean metadata (remove non-string/int/float/bool values)
    
collection.add(
    ids = [chunk.id for chunk],
    embeddings = [embedding for chunk],
    documents = [chunk.text for chunk],
    metadatas = [chunk.metadata for chunk]
)
```

#### `search(query_embedding, collection_name, top_k, filters)`

```python
collection.query(
    query_embeddings=[query_embedding],
    n_results=top_k,
    where=filters  # e.g., {"document_type": "resume"}
)
```

Returns `List[Chunk]` with ChromaDB distance scores attached.

#### `get_chunks(collection_name, filters)`

Retrieves all chunks matching optional metadata filters. Used by `HiringAnalysisUseCase._get_document_context()` to fetch all chunks for a specific document.

#### `delete_document(document_id, collection_name)`

Deletes all chunks with matching `document_id` metadata from the specified collection.

### Metadata Filtering

ChromaDB supports `$and` filters for multi-condition queries:

```python
filters = {
    "$and": [
        {"document_id": resume_id},
        {"document_type": "resume"}
    ]
}
```

This is used by the hiring analysis pipeline to retrieve chunks for a specific document.

---

> **Next**: [Retrieval Pipeline](09_RETRIEVAL_PIPELINE.md)
