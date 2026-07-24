import traceback
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
import uuid
from backend.infrastructure.database.session import get_db
from backend.infrastructure.database.models import DocumentModel, DocumentProcessingJobModel, ProcessingStatus
from backend.dependencies.core import get_ingest_document_use_case, get_index_repository
from backend.application.use_cases.ingest_document import IngestDocumentUseCase
from backend.core.domain.document import Document, DocumentType
from backend.core.interfaces.index_repository import IIndexRepository

router = APIRouter(prefix="/documents", tags=["documents"])

class DocumentItemDTO(BaseModel):
    id: str
    filename: str
    document_type: str
    upload_date: datetime
    status: str
    chunk_count: int
    indexed: bool
    error_message: Optional[str] = None
    classification_confidence: Optional[float] = None
    classification_status: Optional[str] = None

class DocumentListResponse(BaseModel):
    documents: List[DocumentItemDTO]
    total: int

def process_document_background(
    doc_id: str, 
    content: bytes, 
    filename: str, 
    file_type: str, 
    use_case: IngestDocumentUseCase,
    doc_type_override: Optional[DocumentType] = None
):
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
        
        domain_doc = Document(
            id=doc_id,
            filename=filename,
            file_type=file_type,
            content=content,
            doc_type_override=doc_type_override
        )
        
        chunks_count, doc_type, classification_res = use_case.execute(domain_doc)
        
        job.chunks_count = chunks_count
        
        if doc_type == DocumentType.UNKNOWN:
            job.indexed = False
            job.status = ProcessingStatus.COMPLETED # Completed parsing but not indexed
        else:
            job.indexed = True
            job.status = ProcessingStatus.COMPLETED
            
        doc_model.doc_type = doc_type.value
        
        if classification_res:
            doc_model.classification_confidence = classification_res.get("confidence")
            doc_model.classification_status = "MANUAL" if doc_type_override else "AUTO"
            
        db.commit()
    except Exception as e:
        job.status = ProcessingStatus.FAILED
        job.error_message = str(e)
        print(f"Error processing document {doc_id}:\n{traceback.format_exc()}")
        db.commit()
    finally:
        db.close()

from fastapi import Form
# ... wait, I'll just use Form directly in the signature
@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    document_type: str = Form("auto"),
    db: Session = Depends(get_db),
    use_case: IngestDocumentUseCase = Depends(get_ingest_document_use_case)
):
    ext = file.filename.split('.')[-1].lower() if file.filename else ""
    if ext not in ['pdf', 'docx', 'doc']:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported.")
        
    content = await file.read()
    doc_id = str(uuid.uuid4())
    
    # Save file to disk for reclassification support
    import os
    os.makedirs("uploads", exist_ok=True)
    with open(f"uploads/{doc_id}.{ext}", "wb") as f:
        f.write(content)
    
    doc_model = DocumentModel(
        id=doc_id,
        filename=file.filename,
        file_type=ext
    )
    db.add(doc_model)
    
    job_model = DocumentProcessingJobModel(
        document_id=doc_id,
        status=ProcessingStatus.PENDING
    )
    db.add(job_model)
    db.commit()
    
    doc_type_override = None
    if document_type != "auto":
        try:
            doc_type_override = DocumentType(document_type)
        except ValueError:
            pass
    
    background_tasks.add_task(
        process_document_background,
        doc_id=doc_id,
        content=content,
        filename=file.filename,
        file_type=ext,
        use_case=use_case,
        doc_type_override=doc_type_override
    )
    
    return {
        "document_id": doc_id,
        "status": "processing"
    }

@router.get("", response_model=DocumentListResponse)
async def get_documents(db: Session = Depends(get_db)):
    docs = db.query(DocumentModel).order_by(desc(DocumentModel.uploaded_at)).all()
    results = []
    for doc in docs:
        job = db.query(DocumentProcessingJobModel).filter(DocumentProcessingJobModel.document_id == doc.id).first()
        results.append(DocumentItemDTO(
            id=doc.id,
            filename=doc.filename,
            document_type=doc.doc_type or "unknown",
            upload_date=doc.uploaded_at,
            status=job.status.value.lower() if job else "unknown",
            chunk_count=job.chunks_count if job else 0,
            indexed=job.indexed if job else False,
            error_message=job.error_message if job else None,
            classification_confidence=doc.classification_confidence,
            classification_status=doc.classification_status
        ))
    return DocumentListResponse(documents=results, total=len(results))

@router.get("/{doc_id}")
async def get_document(doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(DocumentModel).filter(DocumentModel.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    job = db.query(DocumentProcessingJobModel).filter(DocumentProcessingJobModel.document_id == doc.id).first()
    return {
        "id": doc.id,
        "filename": doc.filename,
        "document_type": doc.doc_type or "unknown",
        "upload_date": doc.uploaded_at,
        "status": job.status.value.lower() if job else "unknown",
        "chunk_count": job.chunks_count if job else 0,
        "error_message": job.error_message if job else None,
        "classification_confidence": doc.classification_confidence,
        "classification_status": doc.classification_status
    }

@router.get("/{doc_id}/status")
async def get_document_status(doc_id: str, db: Session = Depends(get_db)):
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

@router.delete("/{doc_id}")
async def delete_document(
    doc_id: str, 
    db: Session = Depends(get_db),
    index_repo: IIndexRepository = Depends(get_index_repository)
):
    doc = db.query(DocumentModel).filter(DocumentModel.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    job = db.query(DocumentProcessingJobModel).filter(DocumentProcessingJobModel.document_id == doc.id).first()
    
    if job:
        db.delete(job)
    db.delete(doc)
    db.commit()
    
    # Also delete from ChromaDB
    # It might be in 'resumes' or 'job_descriptions'
    index_repo.delete_document(doc_id, "resumes")
    index_repo.delete_document(doc_id, "job_descriptions")
    
    return {"status": "success", "message": f"Document {doc_id} deleted."}

class ReclassifyRequest(BaseModel):
    document_type: str

@router.post("/{doc_id}/reclassify")
async def reclassify_document(
    doc_id: str,
    request: ReclassifyRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    use_case: IngestDocumentUseCase = Depends(get_ingest_document_use_case),
    index_repo: IIndexRepository = Depends(get_index_repository)
):
    doc = db.query(DocumentModel).filter(DocumentModel.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    job = db.query(DocumentProcessingJobModel).filter(DocumentProcessingJobModel.document_id == doc.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Document job not found")
        
    try:
        doc_type_override = DocumentType(request.document_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document_type")
        
    # Delete existing vectors from ChromaDB to prevent duplication
    # We delete from all collections since we might have indexed it as the wrong type before
    # The unify retrieval uses 'documents' collection, but previously we might have used 'resumes'/'job_descriptions'
    index_repo.delete_document(doc_id, "documents")
    index_repo.delete_document(doc_id, "resumes")
    index_repo.delete_document(doc_id, "job_descriptions")
    
    job.status = ProcessingStatus.PENDING
    job.indexed = False
    job.chunks_count = 0
    db.commit()
    
    import os
    file_path = f"uploads/{doc_id}.{doc.file_type}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=500, detail="Original document file not found for reclassification")
        
    with open(file_path, "rb") as f:
        content = f.read()
    
    # We re-run the ingest background task, bypassing auto-classification
    background_tasks.add_task(
        process_document_background,
        doc_id=doc_id,
        content=content,
        filename=doc.filename,
        file_type=doc.file_type,
        use_case=use_case,
        doc_type_override=doc_type_override
    )
    
    return {"status": "processing", "message": f"Document {doc_id} is being reclassified."}
