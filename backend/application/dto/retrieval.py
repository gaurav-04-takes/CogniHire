from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class RetrieveRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Metadata filters (e.g., document_id, document_type, section_type)")
    top_k: int = 5
    collection_name: str = Field(..., description="Collection to search in ('resumes' or 'job_descriptions')")

class RetrievedChunk(BaseModel):
    chunk_id: str
    document_id: str
    document_type: str
    section_type: Optional[str] = None
    chunk_index: int
    score: Optional[float] = None
    text: str

class RetrieveResponse(BaseModel):
    query: str
    results: List[RetrievedChunk]
