# 11 — Hiring Intelligence

## Overview

The core value proposition of CogniHire is its suite of Hiring Intelligence APIs. Rather than standard RAG chat, these endpoints run structured analytical workflows comparing a Resume against a Job Description (JD).

**Router**: `backend/api/analyze.py`  
**Use Case**: `HiringAnalysisUseCase`  
**Service Layer**: `backend/application/services/analysis/`

## Context Retrieval for Analysis

Unlike the chat pipeline which uses vector search to find *relevant* chunks, the analysis pipeline needs the **complete context** of the documents to make fair assessments.

`HiringAnalysisUseCase._get_document_context()` bypasses standard retrieval and instead fetches **all chunks** for the requested `document_id` directly from ChromaDB using metadata filters.

```python
filters = {
    "$and": [
        {"document_id": document_id},
        {"document_type": doc_type}
    ]
}
```

The resulting chunks are formatted using the standard `ContextBuilder` and passed to the LLM.

## LLM JSON Parsing

All analysis services inherit from `BaseAnalysisService`, which provides:
```python
def _parse_json(self, text: str, model: Type[T]) -> T:
```
This method safely extracts JSON from Markdown blocks (e.g., stripping ` ```json ` tags) and validates it against Pydantic models. All prompts explicitly instruct the LLM: "Respond ONLY with a JSON object matching this schema..."

---

## 1. Match Score Analysis

**Endpoint**: `POST /api/v1/analyze/match`  
**Service**: `MatchScoreService`  
**Prompt**: `match_score`

### Logic
The prompt instructs the LLM to act as a technical recruiter and evaluate the candidate across four weighted dimensions:

1. **Skills (40%)**: Hard skills, tools, and technologies
2. **Experience (30%)**: Years of experience, scope, and domain match
3. **Education (15%)**: Degrees and certifications
4. **Keywords (15%)**: General industry terminology

The LLM is responsible for calculating the scores out of 100 and computing the weighted sum for the `overall_score`.

### Output Model
`MatchScoreResponse` containing per-dimension scores and explanations, an overall summary, and citations.

---

## 2. Missing Skills Analysis

**Endpoint**: `POST /api/v1/analyze/skills`  
**Service**: `MissingSkillsService`  
**Prompt**: `missing_skills`

### Logic
Identifies skills explicitly required in the JD that are entirely absent from the Resume context. For each missing skill, the LLM determines its `impact` (High/Medium/Low) on the candidate's viability and provides a `recommendation`.

### Output Model
`MissingSkillsResponse` containing a list of `SkillGap` objects.

---

## 3. ATS Analysis

**Endpoint**: `POST /api/v1/analyze/ats`  
**Service**: `ATSAnalysisService`  
**Prompt**: `ats_analysis`

### Logic
Simulates an Applicant Tracking System. Extracts all required keywords from the JD, cross-references them against the Resume, and generates lists of present vs. missing keywords. Crucially, it provides actionable recommendations on how the candidate could optimize their resume for ATS software.

### Output Model
`ATSAnalysisResponse` containing lists for `required`, `present`, and `missing` keywords, plus `recommendations`.

---

## 4. Relevant Experience Ranking

**Endpoint**: `None` (Use Case method exists, but not exposed in API)  
**Service**: `RelevantExperienceService`  
**Prompt**: `relevant_experience`

### Logic
Identifies the experience sections from the Resume that best align with the JD requirements. Extracts snippets, explains their alignment, and assigns a rank (1 being most aligned).

### Output Model
`RelevantExperienceResponse` containing a list of `RankedExperience` objects.

---

## 5. Interview Question Generation

**Endpoint**: `POST /api/v1/analyze/interview-questions`  
**Service**: `InterviewQuestionService`  
**Prompt**: `interview_questions`

### Logic
Generates tailored interview questions grounded in the candidate's specific claims and the job's specific requirements. Organized into:
- **Technical**: Assessing hard skills claimed
- **Behavioral**: Assessing soft skills in context
- **Project**: Deep dives into specific projects mentioned

For each question, the LLM provides `expected_answer_guidance` and a `rationale` for why the question matters.

### Output Model
`InterviewQuestionResponse` containing categorized lists of `InterviewQuestion` objects.

---

## 6. Document Summarization

**Endpoint**: `POST /api/v1/analyze/summary`  
**Services**: `ResumeSummaryService`, `JDSummaryService`  
**Prompts**: `summary_resume`, `summary_jd`

### Logic
Generates a concise, grounded summary based strictly on the provided context. Returns a brief 2-3 sentence overview and a list of key bullet points.

### Output Model
`SummaryResponse` containing `summary` and `key_points`.

---

> **Next**: [API Reference](12_API_REFERENCE.md)
