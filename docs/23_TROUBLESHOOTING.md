# 23 — Troubleshooting

This guide covers common errors encountered during development and deployment of CogniHire.

## Document Ingestion Issues

### "Document stays in PENDING state forever"
- **Cause**: The FastAPI `BackgroundTasks` runner might have crashed, or you restarted the server while a document was processing.
- **Fix**: Delete the document from the UI and re-upload it. Background tasks do not resume on server restart.

### "Document is COMPLETED but indexed=False"
- **Cause**: The classifier scored the document as `UNKNOWN` (neither clearly a Resume nor a JD). UNKNOWN documents are parsed but not indexed into ChromaDB to prevent polluting the vector space.
- **Fix**: On the Upload page, find the document marked "UNKNOWN", select its true type from the dropdown, and click "Save & Index" to trigger a reclassification.

### "Empty text extracted from PDF"
- **Cause**: The PDF is a scanned image, not a text document. PyMuPDF (`fitz`) does not perform OCR.
- **Fix**: The document must be passed through an OCR tool before uploading to CogniHire.

## Analysis & Chat Issues

### "Error 400: Document is not indexed"
- **Cause**: Attempted to run a Match Score or Chat on an UNKNOWN document.
- **Fix**: Reclassify the document first.

### "Chat stream stops abruptly"
- **Cause**: Gemini hit its `max_tokens` limit mid-sentence, or an unexpected network drop occurred.
- **Fix**: Increase `GEMINI_MAX_TOKENS` in `.env`.

### "JSONDecodeError during analysis"
- **Cause**: The LLM returned conversational text instead of strict JSON, breaking `_parse_json()`.
- **Fix**: This is rare due to strict prompt instructions. Try running the analysis again. If it persists, review the prompt in `prompts.json` to ensure the schema instructions are clear.

## Database & Environment Issues

### "sqlite3.OperationalError: no such table"
- **Cause**: The database schema hasn't been created.
- **Fix**: Delete `cognihire.db` and restart the FastAPI server (it automatically calls `Base.metadata.create_all`).

### "ModuleNotFoundError: No module named 'backend'"
- **Cause**: Running scripts from the wrong directory, or PYTHONPATH is not set.
- **Fix**: Always run commands from the repository root directory.
  - Correct: `uvicorn backend.main:app`
  - Incorrect: `cd backend && uvicorn main:app`

### "401 Unauthorized from Google"
- **Cause**: Invalid or missing `GEMINI_API_KEY`.
- **Fix**: Verify your key in `.env`. Ensure you haven't exceeded your API quota in Google AI Studio.

---

> **Next**: [Development Guide](24_DEVELOPMENT_GUIDE.md)
