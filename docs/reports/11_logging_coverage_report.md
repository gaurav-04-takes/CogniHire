# Logging Coverage Report

## 1. Executive Summary
This report validates the implementation of `LoggingService` across CogniHire, verifying that critical business flows and error boundaries emit structured, parsable JSON logs for downstream observability platforms (e.g., Datadog, ELK).

## 2. Coverage Validation

### 2.1 Document Upload & Ingestion
- **Coverage:** ✅ `INFO` level logs emit upon successful file reception.
- **Coverage:** ✅ `DEBUG` level logs emit upon chunk generation and metadata extraction.
- **Coverage:** ✅ `ERROR` level logs emit (with stack traces appended to the JSON object) if the ingestion background task fails.

### 2.2 Retrieval & Reranking
- **Coverage:** ✅ Cache hits and misses are tracked via `DEBUG` logs in `CacheService`.
- **Coverage:** ✅ RRF and Cross-Encoder execution boundaries are traceable (especially if `LANGCHAIN_TRACING_V2=true` is enabled, which offloads the granular spans to LangSmith).

### 2.3 Prompt Execution & LLM Calls
- **Coverage:** ✅ `PromptManager` successfully traces prompt template retrievals.
- **Coverage:** ✅ `GeminiProvider` effectively catches and logs `google.api_core.exceptions` or network connectivity issues at the `ERROR` level before bubbling them up to the API.
- **Context:** Logs include the exception trace, model parameter (`gemini-2.5-pro`), and latency of the failed request.

### 2.4 Feedback & Evaluation
- **Coverage:** ✅ `INFO` logs are emitted in `api/feedback.py` containing the `record.id` and `record.score` for real-time tracking of user sentiment.
- **Coverage:** ✅ `EvaluationService` emits `INFO` logs when quality gates pass, and `WARNING` logs if a generated response fails the 0.70 threshold for Faithfulness/Relevancy.

## 3. Formatting standard
All logs are processed via `JSONFormatter` guaranteeing:
`{"timestamp": "...", "name": "cognihire", "level": "INFO", "message": "...", "exception": null}`

## 4. Conclusion
The logging coverage satisfies enterprise observability requirements, providing sufficient diagnostic traces for both application telemetry and security auditing.
