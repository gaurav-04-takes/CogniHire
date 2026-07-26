"""
Section-aware document chunker.

Architectural layer:
    Infrastructure.

Purpose:
    Divides parsed documents into smaller text chunks suitable for embedding,
    while explicitly preserving semantic section boundaries.

Data flow:
    Receives a ParsedDocument containing sections. Outputs a list of Chunk
    domain objects with deterministic metadata.

Key dependencies:
    - LangChain RecursiveCharacterTextSplitter
    - Chunk, ParsedDocument domain models.

Related modules:
    - backend.application.use_cases.ingest_document
"""
from typing import List, Dict, Any
from backend.core.domain.document import ParsedDocument
from backend.core.domain.chunk import Chunk
from langchain_text_splitters import RecursiveCharacterTextSplitter
import uuid

class SectionAwareChunker:
    """
    Splits text recursively while adhering to previously extracted sections.
    """
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        # We use recursive text splitter as a fallback *within* a section if it exceeds chunk_size
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )

    def chunk_document(self, doc: ParsedDocument) -> List[Chunk]:
        """
        Chunks a ParsedDocument, preserving section boundaries.
        Each section is chunked independently.

        Overlap is applied only within the current section. Text from Education
        must never be merged into an Experience chunk.

        Args:
            doc: The ParsedDocument containing semantic sections.

        Returns:
            A list of Chunk objects representing the document. The chunk index
            is stable within a document and appears in user-facing citations.
        """
        chunks = []
        chunk_idx = 0
        
        for section in doc.sections:
            # Split the section content if it's too long, else it remains one chunk
            section_texts = self.text_splitter.split_text(section.content)
            
            for text in section_texts:
                metadata = {
                    "document_id": doc.document_id,
                    "document_type": doc.doc_type.value,
                    "section_type": section.title,
                    "chunk_index": chunk_idx
                }
                # Merge document-level metadata
                metadata.update(doc.metadata)
                
                # Advance the chunk index so citations preserve the original
                # ordering of chunks within the document section.
                chunk = Chunk(
                    id=f"{doc.document_id}_chunk_{chunk_idx}",
                    document_id=doc.document_id,
                    doc_type=doc.doc_type,
                    section_type=section.title,
                    text=text,
                    metadata=metadata
                )
                chunks.append(chunk)
                chunk_idx += 1
                
        return chunks
