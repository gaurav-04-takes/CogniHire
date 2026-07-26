# 24 — Development Guide

This guide explains how to extend CogniHire without violating its Clean Architecture principles.

## 1. Adding a New LLM Provider (e.g., OpenAI)

Thanks to Clean Architecture, you can swap Gemini for OpenAI without touching the business logic.

1. **Create the implementation**:
   Create `backend/infrastructure/llm/openai_provider.py` implementing `ILLMProvider`.
   ```python
   class OpenAIProvider(ILLMProvider):
       def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
           # Call OpenAI API
           return response
   ```

2. **Wire it in DI**:
   In `backend/dependencies/core.py`, replace the GeminiProvider initialization:
   ```python
   # Old
   # llm_provider = GeminiProvider(...)
   
   # New
   llm_provider = OpenAIProvider(api_key=settings.OPENAI_API_KEY)
   ```
   The entire application will now use OpenAI.

## 2. Adding a New Document Type

If you want the system to parse Cover Letters:

1. **Update Domain**:
   Add to `DocumentType` enum in `backend/core/domain/document.py`:
   ```python
   COVER_LETTER = "cover_letter"
   ```

2. **Update Classifier**:
   Add indicators for Cover Letters in `RuleBasedDocumentClassifier`. Update the scoring algorithm to check `cover_letter_score`.

3. **Update Parsers**:
   Update `RuleBasedSectionParser` to recognize cover letter sections (e.g., "To Hiring Manager"). Update `MetadataExtractor`.

4. **Update Frontend**:
   Add "Cover Letter" to the selectboxes in `01_upload.py`.

## 3. Adding a New Hiring Intelligence Feature

If you want to add a "Culture Fit Analysis" endpoint:

1. **Create the Service**:
   Create `backend/application/services/analysis/culture_fit.py`. Inherit from `BaseAnalysisService`. Define a Pydantic output model `CultureFitResponse`.

2. **Create the Prompt**:
   Add a `culture_fit` key to `backend/prompts/prompts.json` with the strict JSON schema matching your Pydantic model.

3. **Create the Use Case Method**:
   Add `generate_culture_fit()` to `HiringAnalysisUseCase` in `backend/application/use_cases/hiring_analysis_pipeline.py`.

4. **Create the Endpoint**:
   Add `@router.post("/culture-fit")` to `backend/api/analyze.py`.

5. **Update Frontend**:
   Add a new tab in `pages/02_analyze.py` to call the endpoint and render the data.

## 4. Updating the Database Schema

1. Modify `backend/infrastructure/database/models.py`.
2. Generate an Alembic migration:
   ```bash
   alembic revision --autogenerate -m "Added new column"
   ```
3. Apply the migration:
   ```bash
   alembic upgrade head
   ```

## 5. Architectural Rules to Remember

- **Never import `backend.infrastructure` into `backend.application`** (except in `dependencies/core.py`).
- **Never put API logic (HTTP requests, FastAPI `Depends`) into Use Cases.**
- **All new prompts must go in `prompts.json`. Do not hardcode prompts in Python files.**
- **Frontend files must never import backend code.** They must use `requests` (via `APIClient`).

---

> **Next**: [Glossary](25_GLOSSARY.md)
