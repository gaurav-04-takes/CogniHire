# 20 — Testing Guide

CogniHire uses `pytest` for all backend testing, with `pytest-asyncio` for async routes and `pytest-mock` for dependency mocking.

**Directory**: `backend/tests/`

## Test Structure

| File | Type | Coverage |
|------|------|----------|
| `test_bge_embedder.py` | Unit | Tests `BGEEmbeddingProvider` (Gemini embeddings) |
| `test_chat_api.py` | API / Integration | Tests `/chat` router and streaming logic |
| `test_analyze_api.py` | API / Integration | Tests `/analyze` router and validation logic |
| `test_documents_api.py` | API / Integration | Tests upload, reclassify, delete endpoints |

## Running Tests

Run all tests:
```bash
pytest
```

Run tests with verbose output and coverage report:
```bash
pytest -v --cov=backend
```

Run tests matching a specific pattern:
```bash
pytest -k "chat"
```

## Configuration (`pytest.ini`)

The `pytest.ini` file in the root directory defines the configuration:
```ini
[pytest]
testpaths = backend/tests
asyncio_mode = auto
addopts = --strict-markers -v
markers =
    unit: marks unit tests
    integration: marks integration tests
    api: marks api tests
    slow: marks slow-running tests
```

## Mocking Strategy

Because the application relies heavily on third-party APIs (Gemini) and databases (ChromaDB, SQLite), most tests mock the infrastructure layer.

### Example: Mocking the LLM
In `test_analyze_api.py`, the LLM provider is mocked to prevent actual API calls during testing:

```python
@patch('backend.application.services.analysis.match_score.GeminiProvider')
def test_match_score(mock_gemini, client, db_session):
    mock_gemini.return_value.generate.return_value = '{"overall_score": 85}'
    # ... test logic ...
```

### Dependency Overrides
FastAPI's dependency override feature is used in API tests to inject test databases or mocked use cases:

```python
app.dependency_overrides[get_db_session] = override_get_db
```

## Coverage Thresholds

The `.coveragerc` file enforces a minimum coverage threshold of **85%**. If coverage falls below this, the test suite will exit with a failure code, breaking the CI/CD pipeline.

Files excluded from coverage:
- `backend/tests/*`
- `backend/migrations/*`
- `venv/*`

---

> **Next**: [SonarQube Guide](21_SONARQUBE_GUIDE.md)
