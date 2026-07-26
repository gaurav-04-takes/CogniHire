# 05 — Domain Models

All domain models are defined using Pydantic `BaseModel` and reside in `backend/core/domain/`.

---

## DocumentType (Enum)

**File**: `backend/core/domain/document.py`

```python
class DocumentType(str, Enum):
    RESUME = "resume"
    JOB_DESCRIPTION = "job_description"
    UNKNOWN = "unknown"
```

| Value | Meaning |
|-------|---------|
| `resume` | Document classified as a candidate resume |
| `job_description` | Document classified as a job description |
| `unknown` | Classifier could not determine the type; requires manual classification |

**Used by**: Classification, section parsing, chunking metadata, ChromaDB filters, analysis validation.

---

## ClassificationResult

**File**: `backend/core/domain/document.py`

| Field | Type | Description |
|-------|------|-------------|
| `document_type` | `DocumentType` | The determined classification |
| `confidence` | `float` | `abs(resume_score - jd_score)` — higher means more confident |
| `resume_score` | `float` | Total weighted resume indicator score |
| `job_description_score` | `float` | Total weighted JD indicator score |
| `matched_indicators` | `Dict[str, List[str]]` | Keys: `resume`, `job_description`, `weak`. Values: matched keyword lists |

**Example**:
```json
{
  "document_type": "resume",
  "confidence": 5.0,
  "resume_score": 7.1,
  "job_description_score": 2.1,
  "matched_indicators": {
    "resume": ["professional summary", "work experience", "certifications", "email_address"],
    "job_description": ["skills"],
    "weak": ["skills", "experience", "education"]
  }
}
```

---

## Document

**File**: `backend/core/domain/document.py`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | required | UUID identifier |
| `filename` | `str` | required | Original upload filename |
| `file_type` | `str` | required | File extension: `pdf`, `docx`, `doc` |
| `content` | `bytes` | required | Raw file bytes (not repr'd) |
| `doc_type_override` | `Optional[DocumentType]` | `None` | Manual classification override |
| `uploaded_at` | `datetime` | `datetime.utcnow()` | Upload timestamp |

**Purpose**: Represents a raw uploaded document before processing. Created in the API layer and passed to `IngestDocumentUseCase`.

---

## ParsedDocument

**File**: `backend/core/domain/document.py`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `document_id` | `str` | required | Links to parent Document.id |
| `doc_type` | `DocumentType` | required | Classified type (or overridden) |
| `text_content` | `str` | required | Cleaned, normalized full text |
| `sections` | `List[DocumentSection]` | `[]` | Detected sections |
| `metadata` | `Dict[str, Any]` | `{}` | Extracted metadata (name, years of experience, education) |

**Lifecycle**: Created by parser (with `doc_type=UNKNOWN`) → classifier sets `doc_type` → metadata extractor populates `metadata` → section parser populates `sections`.

---

## DocumentSection

**File**: `backend/core/domain/document.py`

| Field | Type | Description |
|-------|------|-------------|
| `title` | `str` | Section heading (e.g., "Experience", "Education", "Required Skills") |
| `content` | `str` | Raw text content of the section |
| `start_char_idx` | `int` | Starting character index in the original text |
| `end_char_idx` | `int` | Ending character index in the original text |

**Example**:
```json
{
  "title": "Experience",
  "content": "Experience\nSenior Software Engineer at TechCorp (2020-2024)\n...",
  "start_char_idx": 245,
  "end_char_idx": 1023
}
```

---

## Chunk

**File**: `backend/core/domain/chunk.py`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | required | `{document_id}_chunk_{index}` |
| `document_id` | `str` | required | Parent document ID |
| `doc_type` | `DocumentType` | required | Parent document type |
| `section_type` | `Optional[str]` | `None` | Section this chunk belongs to (e.g., "Experience") |
| `text` | `str` | required | The actual text content |
| `metadata` | `Dict[str, Any]` | `{}` | Additional metadata for filtering |
| `score` | `Optional[float]` | `None` | Populated during retrieval/reranking |

**Metadata contents** (populated during chunking):
- `document_id`: string
- `document_type`: string (`resume` or `job_description`)
- `section_type`: string (e.g., "Skills", "Experience")
- `chunk_index`: integer
- Plus any document-level metadata (years_of_experience, education_level, etc.)
- `embedding`: list of floats (temporarily attached, removed before ChromaDB storage)

---

## Citation

**File**: `backend/core/domain/chat.py`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `document_id` | `str` | required | Source document ID |
| `document_type` | `str` | required | `resume` or `job_description` |
| `section_type` | `str` | required | Section name (e.g., "Experience") |
| `chunk_index` | `int` | required | Chunk number within the document |
| `page` | `Optional[int]` | `None` | Page number (if available from metadata) |

**Format method**: `citation.format()` → `[Resume | Experience | Page 2 | Chunk 6]`

---

## ChatMessage

**File**: `backend/core/domain/chat.py`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `role` | `str` | required | `user`, `assistant`, or `system` |
| `content` | `str` | required | Message text |
| `citations` | `List[Citation]` | `[]` | Attached citations (for assistant messages) |
| `timestamp` | `datetime` | `datetime.utcnow()` | Message timestamp |

---

## ChatSession

**File**: `backend/core/domain/chat.py`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `session_id` | `str` | required | UUID identifier |
| `history` | `List[ChatMessage]` | `[]` | Ordered message history |
| `rewritten_queries` | `List[str]` | `[]` | All rewritten queries for this session |
| `created_at` | `datetime` | `datetime.utcnow()` | Session creation time |
| `updated_at` | `datetime` | `datetime.utcnow()` | Last update time |

**Persistence**: In-memory only (via `MemoryChatSessionRepository`). Lost on server restart.

---

## ProcessingStatus (SQLAlchemy Enum)

**File**: `backend/infrastructure/database/models.py`

```python
class ProcessingStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
```

**State transitions**:
```
PENDING → PROCESSING → COMPLETED
PENDING → PROCESSING → FAILED
```

On reclassification: `COMPLETED/FAILED → PENDING → PROCESSING → COMPLETED/FAILED`

---

## Analysis Response Models

All defined in `backend/application/services/analysis/`.

### MatchScoreResponse
| Field | Type | Description |
|-------|------|-------------|
| `overall_score` | `float` | 0–100 weighted score |
| `skills` | `MatchDimension` | Score + explanation (40% weight) |
| `experience` | `MatchDimension` | Score + explanation (30% weight) |
| `education` | `MatchDimension` | Score + explanation (15% weight) |
| `keywords` | `MatchDimension` | Score + explanation (15% weight) |
| `explanation` | `str` | Overall summary |
| `citations` | `List[str]` | Formatted citation strings |

### MatchDimension
| Field | Type |
|-------|------|
| `score` | `float` (0–100) |
| `explanation` | `str` |

### MissingSkillsResponse
| Field | Type |
|-------|------|
| `missing_skills` | `List[SkillGap]` |
| `explanation` | `str` |
| `citations` | `List[str]` |

### SkillGap
| Field | Type |
|-------|------|
| `skill` | `str` |
| `impact` | `str` (High/Medium/Low) |
| `recommendation` | `str` |

### ATSAnalysisResponse
| Field | Type |
|-------|------|
| `required_keywords` | `List[str]` |
| `present_keywords` | `List[str]` |
| `missing_keywords` | `List[str]` |
| `recommendations` | `List[str]` |
| `explanation` | `str` |
| `citations` | `List[str]` |

### RelevantExperienceResponse
| Field | Type |
|-------|------|
| `ranked_experiences` | `List[RankedExperience]` |
| `overall_explanation` | `str` |
| `citations` | `List[str]` |

### RankedExperience
| Field | Type |
|-------|------|
| `experience_snippet` | `str` |
| `alignment_explanation` | `str` |
| `rank` | `int` |

### InterviewQuestionResponse
| Field | Type |
|-------|------|
| `technical_questions` | `List[InterviewQuestion]` |
| `behavioral_questions` | `List[InterviewQuestion]` |
| `project_questions` | `List[InterviewQuestion]` |
| `explanation` | `str` |
| `citations` | `List[str]` |

### InterviewQuestion
| Field | Type |
|-------|------|
| `question` | `str` |
| `expected_answer_guidance` | `str` |
| `rationale` | `str` |

### SummaryResponse
| Field | Type |
|-------|------|
| `summary` | `str` |
| `key_points` | `List[str]` |
| `citations` | `List[str]` |

---

> **Next**: [Ingestion Pipeline](06_INGESTION_PIPELINE.md)
