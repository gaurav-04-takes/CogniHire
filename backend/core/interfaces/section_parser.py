from abc import ABC, abstractmethod
from typing import List
from ..domain.document import DocumentSection

class ISectionParser(ABC):
    @abstractmethod
    def parse_sections(self, text: str, doc_type: str) -> List[DocumentSection]:
        """Parse raw text into semantic sections based on document type."""
        pass
