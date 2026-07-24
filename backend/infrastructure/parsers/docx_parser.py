from docx import Document as DocxDocument
import io
import re
from typing import Dict, Any
from backend.core.interfaces.parser import IDocumentParser
from backend.core.domain.document import Document, ParsedDocument, DocumentType

class DOCXDocumentParser(IDocumentParser):
    def parse(self, document: Document) -> ParsedDocument:
        """
        Parses a DOCX document using python-docx.
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
        """Removes page artifacts and normalizes spacing."""
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
