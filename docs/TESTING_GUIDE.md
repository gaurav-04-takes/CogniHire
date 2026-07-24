# Testing Guide

CogniHire utilizes `pytest` for all backend testing. 

## Running Tests
Ensure your virtual environment is active and run:
```bash
# Add backend to python path for module resolution
export PYTHONPATH="."
pytest backend/tests/
```

## Test Structure
- **Unit Tests:** Focus on isolated logic in `backend/core/services/` (e.g., `EvaluationService`, `CacheService`).
- **Integration Tests:** (Planned) Will use `testcontainers-python` to spin up ephemeral ChromaDB instances and mock the Gemini API to test the full pipeline.

## Generating Coverage
```bash
pytest --cov=backend backend/tests/
```
Target coverage is 90%+.
