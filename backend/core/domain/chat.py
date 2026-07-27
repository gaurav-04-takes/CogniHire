from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class Citation(BaseModel):
    document_id: str
    document_type: str
    section_type: str
    chunk_index: int
    page: Optional[int] = None
    
    def format(self) -> str:
        """Format as: [Resume | Experience | Page 2 | Chunk 6]"""
        page_str = f" | Page {self.page}" if self.page else ""
        return f"[{self.document_type.title()} | {self.section_type.title()}{page_str} | Chunk {self.chunk_index}]"

class ChatMessage(BaseModel):
    role: str # 'user', 'assistant', 'system'
    content: str
    citations: List[Citation] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatSession(BaseModel):
    session_id: str
    resume_document_id: Optional[str] = None
    jd_document_id: Optional[str] = None
    history: List[ChatMessage] = Field(default_factory=list)
    rewritten_queries: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
