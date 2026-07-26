"""
DOCX parsing implementation.

Architectural layer:
    Infrastructure.

Purpose:
    Extracts text and applies simplistic structure normalization to Microsoft 
    Word (.docx) files using the python-docx library.

Data flow:
    Receives raw DOCX byte content from the document ingestion pipeline.
    Returns a ParsedDocument containing normalized string content.

Key dependencies:
    - python-docx (as docx)

Side effects:
    - In-memory extraction (no direct file writes).

Related modules:
    - backend.core.interfaces.parser
"""
from docx import Document as DocxDocument
import io
import re
from typing import Dict, Any
from backend.core.interfaces.parser import IDocumentParser
from backend.core.domain.document import Document, ParsedDocument, DocumentType

class DOCXDocumentParser(IDocumentParser):
    """
    Parses a DOCX document using python-docx.
    
    Belongs to the infrastructure layer. Instances are injected where
    IDocumentParser is required for DOCX processing.
    """
    def parse(self, document: Document) -> ParsedDocument:
        """
        Parses a DOCX document using python-docx.

        Reads the raw byte stream from the Document domain model and iterates
        through paragraphs. Basic list and heading styles are translated into
        simple Markdown-like text equivalents.

        Args:
            document: The Document domain object containing DOCX bytes.

        Returns:
            A ParsedDocument containing the extracted text. The doc_type is
            initially UNKNOWN, and sections are left empty for the downstream
            pipeline to populate.

        Raises:
            RuntimeError: If python-docx cannot read the byte stream.
        """
        text_content = ""
        metadata: Dict[str, Any] = {}
        
        try:
            # Load docx from bytes
            docx_file = io.BytesIO(document.content)
            doc = DocxDocument(docx_file)
            
            # Extract paragraphs
            for para in doc.paragraphs:
                text = para.text.strip()
                if text:
                    # Check if it's a heading (simplistic check based on style name)
                    if para.style.name.startswith('Heading'):
                        text_content += f"\n\n{text}\n"
                    # Check if it's a list bullet
                    elif 'List Bullet' in para.style.name or para.style.name.startswith('List'):
                        text_content += f"- {text}\n"
                    else:
                        text_content += f"{text}\n"
                        
            # Normalize whitespace
            text_content = self._clean_text(text_content)
            
        except Exception as e:
            raise RuntimeError(f"Failed to parse DOCX document {document.id}: {str(e)}")
            
        return ParsedDocument(
            document_id=document.id,
            doc_type=DocumentType.UNKNOWN,
            text_content=text_content,
            sections=[],
            metadata=metadata
        )

    def _clean_text(self, text: str) -> str:
        """
        Removes page artifacts and normalizes spacing.
        
        Collapse repeated horizontal whitespace while preserving line boundaries.
        Section detection relies on headings remaining on separate lines.
        """
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
