from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from .document import DocumentType

class Chunk(BaseModel):
    id: str = Field(..., description="Unique identifier for this chunk")
    document_id: str = Field(..., description="ID of the parent document")
    doc_type: DocumentType = Field(..., description="Type of the parent document")
    section_type: Optional[str] = Field(None, description="The section this chunk belongs to (e.g., 'Experience')")
    text: str = Field(..., description="The actual text content of the chunk")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for filtering")
    
    # Retrieval scores (populated during search/reranking)
    score: Optional[float] = Field(None, description="Similarity or reranking score")
