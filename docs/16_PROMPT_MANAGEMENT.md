# 16 — Prompt Management

All LLM prompts used across the system are stored in a single JSON file. This separates prompt engineering from business logic and allows easy versioning.

**File**: `backend/prompts/prompts.json`  
**Manager**: `backend/core/services/prompt_manager.py` (`PromptManager`)

## Loading and Usage

The `PromptManager` reads the JSON file on initialization. Services request prompts by key:

```python
prompt_template = prompt_manager.get_prompt("match_score")
formatted_prompt = prompt_template.format(resume_context=..., jd_context=...)
```

## Prompt Catalogue

### 1. `chat_generation`
- **Purpose**: Multi-turn chat assistant.
- **Variables**: `{context}`, `{query}`
- **Key instruction**: "Answer the user's question based ONLY on the provided context... If the answer is not in the context, state that you don't know."

### 2. `query_rewriter`
- **Purpose**: Converts follow-up questions containing pronouns into standalone queries for the retriever.
- **Variables**: `{history}`, `{query}`
- **Key instruction**: "Rewrite the final follow-up question to be a standalone query... Do not answer the question."

### 3. `match_score`
- **Purpose**: Calculates resume-to-JD match score across 4 dimensions.
- **Variables**: `{resume_context}`, `{jd_context}`
- **Key instruction**: "Evaluate the candidate based on: Skills (40%), Experience (30%), Education (15%), Keywords (15%). Respond ONLY with a JSON object..."

### 4. `missing_skills`
- **Purpose**: Identifies skills required by the JD that are absent from the resume.
- **Variables**: `{resume_context}`, `{jd_context}`
- **Key instruction**: "Identify skills explicitly required in the JD that are missing from the resume. Determine impact (High/Medium/Low)."

### 5. `ats_analysis`
- **Purpose**: Simulates an ATS keyword parser to help candidates optimize their resumes.
- **Variables**: `{resume_context}`, `{jd_context}`
- **Key instruction**: "Extract required keywords from JD and cross-reference with the Resume. Provide actionable recommendations."

### 6. `relevant_experience`
- **Purpose**: Ranks the candidate's experience snippets against the JD.
- **Variables**: `{resume_context}`, `{jd_context}`
- **Key instruction**: "Identify experience sections from the Resume that best align with the JD requirements. Rank them from most to least aligned."

### 7. `interview_questions`
- **Purpose**: Generates tailored technical, behavioral, and project questions.
- **Variables**: `{resume_context}`, `{jd_context}`
- **Key instruction**: "Generate interview questions grounded in the candidate's specific claims and the job's specific requirements."

### 8. `summary_resume` & `summary_jd`
- **Purpose**: Creates concise overviews of the documents.
- **Variables**: `{context}`
- **Key instruction**: "Provide a 2-3 sentence overview and a list of key bullet points."

## JSON Format Requirements

The LLM is highly sensitive to the requested JSON schema. All analysis prompts end with a strict JSON format template that perfectly mirrors the corresponding Pydantic response models in `backend/application/services/analysis/`.

Example output schema instruction from `missing_skills`:
```json
{
  "missing_skills": [
    {"skill": "string", "impact": "High|Medium|Low", "recommendation": "string"}
  ],
  "explanation": "string",
  "citations": []
}
```

---

> **Next**: [Observability & Evaluation](17_OBSERVABILITY_AND_EVALUATION.md)
