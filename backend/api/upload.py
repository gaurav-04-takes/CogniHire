"""
FastAPI Upload Routes.

Architectural layer:
    API (Controllers).

Purpose:
    Exposes a legacy or alternative endpoint for uploading documents.
    Handles basic file validation and queues background ingestion.

Data flow:
    FastAPI File -> Validation -> Save to DB as PENDING -> Background IngestDocumentUseCase

Key dependencies:
    - backend.infrastructure.database.models
    - backend.application.use_cases.ingest_document
"""
import traceback
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
from backend.infrastructure.database.session import get_db
from backend.infrastructure.database.models import DocumentModel, DocumentProcessingJobModel, ProcessingStatus
from backend.config.settings import settings
from backend.dependencies.core import get_ingest_document_use_case
from backend.application.use_cases.ingest_document import IngestDocumentUseCase
from backend.core.domain.document import Document

router = APIRouter(prefix="/documents", tags=["documents"])

def process_document_background(
    doc_id: str, 
    content: bytes, 
    filename: str, 
    file_type: str, 
    use_case: IngestDocumentUseCase
):
    """
    Background worker function that executes the ingestion pipeline.
    Must maintain its own DB session since FastAPI closes the request session.
    """
    # Need a fresh DB session for background task
    from backend.infrastructure.database.session import SessionLocal
    db = SessionLocal()
    
    job = db.query(DocumentProcessingJobModel).filter(DocumentProcessingJobModel.document_id == doc_id).first()
    doc_model = db.query(DocumentModel).filter(DocumentModel.id == doc_id).first()
    
    if not job or not doc_model:
        db.close()
        return
        
    try:
        job.status = ProcessingStatus.PROCESSING
        db.commit()
        
        # Build Domain Document
        domain_doc = Document(
            id=doc_id,
            filename=filename,
            file_type=file_type,
            content=content
        )
        
        # Execute Pipeline
        chunks_count = use_case.execute(domain_doc)
        
        # Update Job Status
        job.chunks_count = chunks_count
        job.indexed = True
        job.status = ProcessingStatus.COMPLETED
        
        # Also update doc type in DB based on what pipeline determined if possible
        # We don't have a direct return of the parsed doc from use_case.execute, 
        # but in a fuller implementation we might return a DTO.
        
        db.commit()
    except Exception as e:
        job.status = ProcessingStatus.FAILED
        job.error_message = str(e)
        print(f"Error processing document {doc_id}:\n{traceback.format_exc()}")
        db.commit()
    finally:
        db.close()

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    use_case: IngestDocumentUseCase = Depends(get_ingest_document_use_case)
):
    """
    Accepts file uploads, applies size and magic byte validation, and queues background processing.
    """
    # Validate extension
    ext = file.filename.split('.')[-1].lower() if file.filename else ""
    if ext not in ['pdf', 'docx', 'doc']:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported.")
        
    content = await file.read()
    
    # 1. File Size Validation
    max_size_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(content) > max_size_bytes:
        raise HTTPException(status_code=413, detail=f"File exceeds maximum upload size of {settings.MAX_UPLOAD_SIZE_MB}MB.")
        
    # 2. Basic Magic Bytes Validation (simplified for V1)
    if ext == 'pdf' and not content.startswith(b'%PDF'):
        raise HTTPException(status_code=400, detail="Invalid PDF file format.")
    elif ext in ['docx', 'doc'] and not content.startswith(b'PK'): # DOCX is a zip file
        raise HTTPException(status_code=400, detail="Invalid DOCX file format.")

    doc_id = str(uuid.uuid4())
    
    # Create Document record
    doc_model = DocumentModel(
        id=doc_id,
        filename=file.filename,
        file_type=ext
    )
    db.add(doc_model)
    
    # Create Job record
    job_model = DocumentProcessingJobModel(
        document_id=doc_id,
        status=ProcessingStatus.PENDING
    )
    db.add(job_model)
    db.commit()
    
    # Launch background task
    background_tasks.add_task(
        process_document_background,
        doc_id=doc_id,
        content=content,
        filename=file.filename,
        file_type=ext,
        use_case=use_case
    )
    
    return {
        "document_id": doc_id,
        "status": "processing"
    }

@router.get("/{doc_id}/status")
async def get_document_status(doc_id: str, db: Session = Depends(get_db)):
    """
    Retrieves the processing status of an uploaded document.
    """
    job = db.query(DocumentProcessingJobModel).filter(DocumentProcessingJobModel.document_id == doc_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Document job not found")
        
    return {
        "document_id": job.document_id,
        "status": job.status.value.lower(),
        "chunks": job.chunks_count,
        "indexed": job.indexed,
        "error": job.error_message
    }
