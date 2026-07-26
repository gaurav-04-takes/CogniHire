"""
Document parsing interface.

Architectural layer:
    Core interfaces.

Purpose:
    Defines the contract for parsing raw documents into structured formats.

Data flow:
    Takes a raw Document entity (often containing binary or raw text data)
    and returns a ParsedDocument containing metadata and semantic sections.

Key dependencies:
    - Document, ParsedDocument domain objects.

Related modules:
    - backend.infrastructure.parsers.pdf_parser
    - backend.infrastructure.parsers.docx_parser
"""
from abc import ABC, abstractmethod
from ..domain.document import Document, ParsedDocument

class IDocumentParser(ABC):
    """
    Defines the abstraction for parsing document content.

    Different implementations handle specific file formats (e.g., PDF, DOCX)
    while conforming to this unified extraction contract.
    """
    @abstractmethod
    def parse(self, document: Document) -> ParsedDocument:
        """
        Parse a raw Document into a ParsedDocument with extracted sections and metadata.

        Args:
            document: The input Document containing raw data or a file path.

        Returns:
            A ParsedDocument containing the structured representation.
            
        Raises:
            ParseError: If the file is corrupt or the format is unsupported.
        """
        pass
