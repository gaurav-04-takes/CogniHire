"""
Document metadata extractor.

Architectural layer:
    Infrastructure (parsing utilities).

Purpose:
    Extracts high-level metadata (e.g., years of experience, education) from 
    Resumes or Job Descriptions using deterministic heuristics and regex.

Data flow:
    Receives classified document text from the ingestion pipeline.
    Returns a dictionary of extracted properties to be merged into DocumentRecord.

Key dependencies:
    None.

Related modules:
    - backend.application.use_cases.ingest_document
"""
import re
from typing import Dict, Any
from backend.core.domain.document import DocumentType

class MetadataExtractor:
    """
    Extracts explicit data fields from unstructured document text.
    """
    def extract(self, text: str, doc_type: DocumentType) -> Dict[str, Any]:
        """
        Extracts metadata deterministically based on document type using regex and heuristics.

        Args:
            text: The full normalized document text.
            doc_type: Indicates whether to look for Resume or JD specific patterns.

        Returns:
            A dictionary containing fields like 'years_of_experience' or 'job_title'.
        """
        if doc_type == DocumentType.RESUME:
            return self._extract_resume_metadata(text)
        elif doc_type == DocumentType.JOB_DESCRIPTION:
            return self._extract_jd_metadata(text)
        return {}

    def _extract_resume_metadata(self, text: str) -> Dict[str, Any]:
        """Apply heuristics to extract resume-specific metadata."""
        metadata = {}
        
        # 1. Years of experience (heuristic: look for "X years")
        yoe_match = re.search(r'(\d+)(?:\+)?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:experience|exp)', text, re.IGNORECASE)
        if yoe_match:
            metadata["years_of_experience"] = int(yoe_match.group(1))
            
        # 2. Education level
        education_levels = ["PhD", "Master", "Bachelor", "B.S.", "B.A.", "M.S.", "MBA"]
        for level in education_levels:
            if re.search(r'\b' + re.escape(level) + r'\b', text, re.IGNORECASE):
                metadata["education_level"] = level
                break
                
        # 3. Candidate Name (Heuristic: first non-empty line of the resume)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            # A very simplistic heuristic for name
            metadata["candidate_name"] = lines[0]
            
        return metadata

    def _extract_jd_metadata(self, text: str) -> Dict[str, Any]:
        """Apply heuristics to extract JD-specific metadata."""
        metadata = {}
        
        # 1. Required years of experience
        yoe_match = re.search(r'(\d+)(?:\+)?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:experience|exp)', text, re.IGNORECASE)
        if yoe_match:
            metadata["required_years_of_experience"] = int(yoe_match.group(1))
            
        # 2. Job Title (Heuristic: first non-empty line)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            metadata["job_title"] = lines[0]
            
        return metadata
