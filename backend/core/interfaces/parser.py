from abc import ABC, abstractmethod
from ..domain.document import Document, ParsedDocument

class IDocumentParser(ABC):
    @abstractmethod
    def parse(self, document: Document) -> ParsedDocument:
        """Parse a raw Document into a ParsedDocument with extracted sections and metadata."""
        pass
