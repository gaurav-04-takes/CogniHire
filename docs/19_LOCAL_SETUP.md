# 19 — Local Setup

This guide walks through setting up the CogniHire development environment from scratch.

## Prerequisites
- Python 3.10+
- Git
- Google Gemini API Key (from Google AI Studio)

## 1. Clone the Repository
```bash
git clone https://github.com/your-username/CogniHire.git
cd CogniHire
```

## 2. Virtual Environment
Create and activate a Python virtual environment to isolate dependencies.

**macOS/Linux**:
```bash
python -m venv venv
source venv/bin/activate
```

**Windows (PowerShell)**:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

## 3. Install Dependencies
Install the required packages.

```bash
# Core dependencies
pip install -r requirements.txt

# Development dependencies (for testing, coverage, mocking)
pip install -r requirements-dev.txt
```

## 4. Environment Configuration
Copy the template environment file:
```bash
cp .env.example .env
```

Open `.env` in a text editor and update at minimum:
```env
# Required for any functionality
GEMINI_API_KEY=your_actual_api_key_here

# Optional: Enable LangSmith Tracing
LANGSMITH_TRACING=true
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=CogniHire
```

## 5. Database Migration (Alembic)
Initialize the SQLite database schema.
```bash
alembic upgrade head
```
*(If Alembic is not configured, FastAPI will create the tables automatically via `Base.metadata.create_all(bind=engine)` in `main.py` when it starts).*

## 6. Run the Backend API
Start the FastAPI server using Uvicorn with auto-reload enabled.
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```
- The API is now running at: `http://localhost:8000/api/v1`
- Swagger UI (interactive docs) is at: `http://localhost:8000/docs`

## 7. Run the Frontend UI
Open a **new terminal window**, activate your virtual environment again, and start Streamlit.
```bash
streamlit run frontend/app.py
```
- Streamlit will automatically open a browser window at `http://localhost:8501`.

## 8. First Run Verification
1. Navigate to the **Upload** page in the Streamlit UI.
2. Upload a sample PDF resume.
3. Wait for the processing status to say `COMPLETED`.
4. Navigate to the **Chat** page and ask "What is this person's name?". You should receive a generated answer with a citation.

---

> **Next**: [Testing Guide](20_TESTING_GUIDE.md)
