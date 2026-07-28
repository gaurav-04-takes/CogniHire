"""
FastAPI Application Entrypoint.

Architectural layer:
    API (Framework Startup).

Purpose:
    Initializes the FastAPI application, mounts the main API router, configures CORS,
    and sets up any required startup/shutdown hooks.

Related modules:
    - backend.api.router
    - backend.config.settings
"""
import os
# Workaround for corporate proxies blocking HuggingFace downloads
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['HF_HUB_DISABLE_SSL_VERIFICATION'] = '1'

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config.settings import settings
from backend.core.services.observability_service import ObservabilityService # Ensure initialized
from backend.api.router import api_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

from fastapi.responses import JSONResponse
from fastapi import Request
from backend.core.domain.exceptions import (
    ApplicationError, ValidationError, DocumentNotFoundError,
    DocumentProcessingError, RetrievalError, LLMProviderError
)
import logging

logger = logging.getLogger(__name__)

@app.exception_handler(ApplicationError)
async def application_error_handler(request: Request, exc: ApplicationError):
    logger.error(f"Application error: {exc.message}")
    status_code = 400
    if isinstance(exc, DocumentNotFoundError):
        status_code = 404
    elif isinstance(exc, (DocumentProcessingError, RetrievalError, LLMProviderError)):
        status_code = 500
    return JSONResponse(
        status_code=status_code,
        content={"detail": exc.message},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
