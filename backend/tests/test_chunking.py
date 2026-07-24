import pytest
from backend.infrastructure.chunkers.section_chunker import SectionAwareChunker
from backend.core.domain.document import ParsedDocument, DocumentSection, DocumentType

def test_chunk_boundary_preservation():
    chunker = SectionAwareChunker(chunk_size=100, chunk_overlap=0)
    
    doc = ParsedDocument(
        document_id="doc1",
        doc_type=DocumentType.RESUME,
        text_content="...",
        sections=[
            DocumentSection(title="Experience", content="Short experience", start_char_idx=0, end_char_idx=10),
            DocumentSection(title="Education", content="Short education", start_char_idx=11, end_char_idx=20)
        ],
        metadata={"candidate_name": "John"}
    )
    
    chunks = chunker.chunk_document(doc)
    
    assert len(chunks) == 2
    assert chunks[0].section_type == "Experience"
    assert chunks[0].text == "Short experience"
    assert chunks[0].metadata["candidate_name"] == "John"
    
    assert chunks[1].section_type == "Education"
    assert chunks[1].text == "Short education"
    
def test_chunk_splitting_long_sections():
    chunker = SectionAwareChunker(chunk_size=20, chunk_overlap=0)
    long_content = "This is a very long section that needs to be split up."
    doc = ParsedDocument(
        document_id="doc1",
        doc_type=DocumentType.RESUME,
        text_content="...",
        sections=[
            DocumentSection(title="Summary", content=long_content, start_char_idx=0, end_char_idx=100)
        ],
        metadata={}
    )
    
    chunks = chunker.chunk_document(doc)
    assert len(chunks) > 1
    assert chunks[0].section_type == "Summary"
    assert chunks[1].section_type == "Summary"
