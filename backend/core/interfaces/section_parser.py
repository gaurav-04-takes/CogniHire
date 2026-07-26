"""
Section parsing interface.

Architectural layer:
    Core interfaces.

Purpose:
    Defines the contract for dividing raw document text into semantic sections.

Data flow:
    Receives continuous text and document type hints, returning a list of
    structured DocumentSection objects.

Key dependencies:
    - DocumentSection domain object.

Related modules:
    - backend.infrastructure.parsers.section_parser
"""
from abc import ABC, abstractmethod
from typing import List
from ..domain.document import DocumentSection

class ISectionParser(ABC):
    """
    Defines the abstraction for semantic section extraction.

    Implementations use rules, regex, or ML models to identify headings
    like 'Education' or 'Experience' in Resumes and JDs.
    """
    @abstractmethod
    def parse_sections(self, text: str, doc_type: str) -> List[DocumentSection]:
        """
        Parse raw text into semantic sections based on document type.

        Args:
            text: The full text of the parsed document.
            doc_type: A hint (Resume or JD) to guide section identification rules.

        Returns:
            A list of DocumentSection objects containing the section heading
            and its corresponding text.
        """
        pass
