# 14 — Frontend Guide

CogniHire's frontend is built entirely in **Streamlit**. It acts as a thin presentation layer, communicating with the backend exclusively via REST API calls.

**Directory**: `frontend/`

---

## Architecture

```mermaid
graph TD
    APP[app.py (Entry)] --> SM[SessionManager]
    APP --> P1[01_upload.py]
    APP --> P2[02_analyze.py]
    APP --> P3[03_chat.py]
    APP --> P4[04_documents.py]
    APP --> P5[05_analytics.py]
    
    P1 -.->|calls| DS[DocumentService]
    P2 -.->|calls| AS[AnalysisService]
    P2 -.->|calls| ES[ExportService]
    P3 -.->|calls| CS[ChatService]
    
    DS -.-> AC[APIClient]
    AS -.-> AC
    ES -.-> AC
    CS -.-> AC
    
    AC -->|HTTP GET/POST| BACKEND[FastAPI Backend]
    
    P2 -.-> W1[match_score_widget]
    P2 -.-> W2[skill_gap_table]
    P3 -.-> W3[citation_card]
    P3 -.-> W4[feedback_widget]
```

---

## Session State Management

**File**: `frontend/state/session_manager.py`

Streamlit re-runs the entire script on every interaction. To persist data across re-runs and page navigations, CogniHire uses a centralized `SessionManager` that wraps `st.session_state`.

### Initialized Keys
`SessionManager.init_state()` is called in `app.py` and initializes:
- `selected_resume_id`: Currently active resume for analysis/chat (UUID)
- `selected_jd_id`: Currently active JD for analysis (UUID)
- `chat_session_id`: UUID of the active chat session (syncs with backend memory repo)
- `messages`: List of chat messages for the UI `st.chat_message` blocks

---

## Service Layer

The frontend service layer encapsulates all HTTP requests to the backend, returning parsed dictionaries.

**File**: `frontend/services/api_client.py`
Provides `APIClient`, a singleton wrapper around the `requests` library configured with the base URL `http://localhost:8000/api/v1`. Includes `get`, `post`, `delete`, and `stream_post` methods.

### Services
1. **`DocumentService`**: Wraps `/documents` endpoints (upload, status polling, list, delete, reclassify).
2. **`AnalysisService`**: Wraps `/analyze` endpoints (match, skills, ATS, interview, summary).
3. **`ChatService`**: Wraps `/chat` endpoints (sync chat, stream chat, history).
4. **`ExportService`**: **Client-side** PDF generation. Takes analysis data dictionaries and uses `fpdf` to generate a downloadable PDF byte stream.

---

## Pages

### 1. Upload (`pages/01_upload.py`)
- Uses `st.file_uploader(accept_multiple_files=True)`
- Allows users to override document classification via selectboxes before upload.
- **Polling Loop**: Once uploaded, displays a spinner and calls `DocumentService.get_status()` every 2 seconds (max 30 times) until the document is `COMPLETED` or `FAILED`.
- **UNKNOWN Handling**: If a document finishes with `UNKNOWN` status (meaning the classifier wasn't confident), it presents a UI to manually classify it and calls the `/reclassify` endpoint.

### 2. Analyze (`pages/02_analyze.py`)
- **Document Selection**: Uses `st.selectbox` to let the user pick one Resume and one JD from the list of completed documents. Updates `SessionManager`.
- **Tabs**: Organizes the massive amount of analysis data into Streamlit tabs:
  - `Match & Summary`: Calls `/match` and `/summary`. Displays gauge charts.
  - `Skills & ATS`: Calls `/skills` and `/ats`. Displays missing skills and keyword analysis.
  - `Interview Prep`: Calls `/interview-questions`. Displays categorized questions.
- **Export**: Provides an `st.download_button` that triggers `ExportService.generate_pdf_report()` and downloads `analysis_report.pdf`.

### 3. Chat (`pages/03_chat.py`)
- Implements a ChatGPT-like interface using `st.chat_message` and `st.chat_input`.
- **Streaming**: Calls `ChatService.chat_stream()`. Uses `st.write_stream()` to display tokens as they arrive.
- **Citations**: Because the backend SSE stream only yields text tokens (and not structured citations), the current streaming implementation lacks citation display. Citations are fully supported in the synchronous endpoint, but the UI currently prioritizes the streaming UX.
- **Feedback**: After an assistant message finishes, renders the `feedback_widget` allowing 1-5 star ratings.

### 4. Documents (`pages/04_documents.py`)
- Fetches all documents and displays them in an `st.dataframe`.
- Provides "Delete" buttons for each document row.

### 5. Analytics (`pages/05_analytics.py`)
- Fetches system metrics from `/analytics/metrics`.
- Uses `plotly.graph_objects` to render a pie chart of document types and a bar chart of processing statuses.
- Displays key performance indicators (KPIs) like average RAGAS scores using `st.metric`.

---

## Components

Reusable UI components located in `frontend/components/`.

| Component | Purpose |
|-----------|---------|
| `citation_card(citations: list)` | Renders an `st.expander` showing structured citation data (document type, section, page, chunk index). |
| `feedback_widget(session_id, index)` | Renders 5 star buttons horizontally. On click, POSTs to the `/feedback` API. |
| `match_score_widget(match_data)` | Renders a Plotly `go.Indicator` gauge chart (0-100) for the overall match score, followed by columns for the dimension breakdown. |
| `skill_gap_table(skills, ats)` | Renders an `st.dataframe` for missing skills, and three columns (Required, Present, Missing) for ATS keywords. |

---

> **Next**: [Configuration Reference](15_CONFIGURATION_REFERENCE.md)
