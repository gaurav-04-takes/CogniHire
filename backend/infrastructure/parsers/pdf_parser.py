"""
PDF parsing implementation.

Architectural layer:
    Infrastructure.

Purpose:
    Extracts text from PDF documents while attempting to preserve layout
    and reading order using PyMuPDF.

Data flow:
    Receives raw PDF byte content from the ingestion pipeline.
    Returns a ParsedDocument containing normalized string content.

Key dependencies:
    - fitz (PyMuPDF)

Side effects:
    - In-memory PDF parsing.

Related modules:
    - backend.core.interfaces.parser
"""
import fitz # PyMuPDF
import re
from typing import Dict, Any
from backend.core.interfaces.parser import IDocumentParser
from backend.core.domain.document import Document, ParsedDocument, DocumentType

class PDFDocumentParser(IDocumentParser):
    """
    Parses a PDF document using PyMuPDF.
    
    Belongs to the infrastructure layer. Configured via dependency injection
    when IDocumentParser is needed for PDF files.
    """
    def parse(self, document: Document) -> ParsedDocument:
        """
        Parses a PDF document using PyMuPDF.
        Extracts raw text while attempting to preserve layout and reading order.

        Preserve page numbers before joining text because citations depend on the
        original page where each chunk was extracted (though we inject it as a text marker).

        Args:
            document: The Document domain object containing PDF bytes.

        Returns:
            A ParsedDocument containing the extracted text. The doc_type is
            initially UNKNOWN, and sections are empty.

        Raises:
            RuntimeError: If PyMuPDF fails to open or read the byte stream.
        """
        text_content = ""
        metadata: Dict[str, Any] = {}
        
        try:
            # fitz.open(stream=bytes, filetype="pdf")
            doc = fitz.open(stream=document.content, filetype="pdf")
            metadata["num_pages"] = doc.page_count
            
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                # Extract text preserving blocks and reading order
                page_text = page.get_text("text")
                text_content += f"\n--- Page {page_num + 1} ---\n"
                text_content += page_text + "\n"
                
            doc.close()
            
            # Clean text: normalize whitespace, remove excessive newlines
            text_content = self._clean_text(text_content)
            
        except Exception as e:
            raise RuntimeError(f"Failed to parse PDF document {document.id}: {str(e)}")
            
        # We don't classify or extract sections here; that happens in the pipeline
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
        # Replace multiple spaces with a single space
        text = re.sub(r' +', ' ', text)
        # Replace 3 or more newlines with double newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
