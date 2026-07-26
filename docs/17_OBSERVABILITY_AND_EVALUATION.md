# 17 — Observability & Evaluation

CogniHire integrates three layers of observability to monitor system health, LLM behavior, and retrieval quality.

## 1. Structured Logging

**Class**: `backend.core.services.logging_service.LoggingService`

All system logs are output as structured JSON rather than plain text. This allows log aggregators (like ELK or Datadog) to parse and index the logs easily.

### Format
```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "name": "CogniHire",
  "level": "INFO",
  "message": "Document ingested successfully",
  "document_id": "uuid",
  "chunks_count": 45
}
```

### Usage
```python
from backend.dependencies.core import logger
logger.info("Message", extra={"key": "value"})
```

---

## 2. LangSmith Tracing

LangSmith provides deep visibility into LLM chains, showing exact prompt inputs, LLM outputs, token usage, and latency for every step.

**Class**: `backend.core.services.observability_service.ObservabilityService`

### Setup
Enabled by setting environment variables in `.env`:
```env
LANGSMITH_TRACING=true
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_key
LANGCHAIN_PROJECT=CogniHire
```

### Initialization
Called in `backend/main.py` on startup:
```python
observability = ObservabilityService()
observability.setup()
```
This function explicitly sets `os.environ` variables so that LangChain's internal hooks automatically trace all calls to `GoogleGenerativeAIEmbeddings` and `ChatGoogleGenerativeAI`.

---

## 3. RAGAS Evaluation (Mocked)

RAGAS (Retrieval Augmented Generation Assessment) is a framework to quantitatively evaluate RAG pipelines.

**Class**: `backend.core.services.evaluation_service.EvaluationService`

### Current Status: Mocked
Real RAGAS evaluation requires making multiple calls to an "evaluator LLM" (typically GPT-4) to score the generated answer against the context. In V1, this is mocked to return hardcoded high scores because evaluator LLM keys were not provisioned.

```python
# From EvaluationService
def evaluate_response(self, ...):
    return {
        "faithfulness": 0.95,
        "answer_relevancy": 0.92,
        "context_precision": 0.88,
        "context_recall": 0.90
    }
```

### Evaluation Trigger
After every chat response, `chat.py` spawns a FastAPI `BackgroundTask` to run the evaluation asynchronously without blocking the user response.

### Metrics Explained
| Metric | What it measures |
|--------|------------------|
| **Faithfulness** | Does the answer hallucinate? (Are all claims grounded in the context?) |
| **Answer Relevancy** | Does the answer actually address the user's query? |
| **Context Precision** | Did the retriever put the most relevant chunks at the top of the list? |
| **Context Recall** | Did the retriever find *all* the relevant information needed? |

---

> **Next**: [Security & Error Handling](18_SECURITY_AND_ERROR_HANDLING.md)
