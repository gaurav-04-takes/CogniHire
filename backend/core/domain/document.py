from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class DocumentType(str, Enum):
    RESUME = "resume"
    JOB_DESCRIPTION = "job_description"
    UNKNOWN = "unknown"

class ClassificationResult(BaseModel):
    document_type: DocumentType
    confidence: float
    resume_score: float
    job_description_score: float
    matched_indicators: Dict[str, List[str]]

class DocumentSection(BaseModel):
    title: str = Field(..., description="Section title (e.g., 'Experience', 'Education', 'Required Skills')")
    content: str = Field(..., description="Raw text content of the section")
    start_char_idx: int = Field(..., description="Starting character index in the original text")
    end_char_idx: int = Field(..., description="Ending character index in the original text")

class Document(BaseModel):
    id: str = Field(..., description="Unique identifier for the document")
    filename: str
    file_type: str = Field(..., description="MIME type or file extension (pdf, docx, txt)")
    content: bytes = Field(..., repr=False)
    doc_type_override: Optional[DocumentType] = Field(default=None, description="Manual classification override")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

class ParsedDocument(BaseModel):
    document_id: str
    doc_type: DocumentType
    text_content: str = Field(..., description="Cleaned, normalized full text")
    sections: List[DocumentSection] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Extracted metadata like name, job title, company, etc.")
