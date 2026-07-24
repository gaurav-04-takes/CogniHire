import re
from typing import List
from backend.core.interfaces.section_parser import ISectionParser
from backend.core.domain.document import DocumentSection, DocumentType

class RuleBasedSectionParser(ISectionParser):
    def parse_sections(self, text: str, doc_type: DocumentType) -> List[DocumentSection]:
        if doc_type == DocumentType.RESUME:
            return self._parse_resume_sections(text)
        elif doc_type == DocumentType.JOB_DESCRIPTION:
            return self._parse_jd_sections(text)
        else:
            # Fallback
            return [DocumentSection(
                title="Content",
                content=text,
                start_char_idx=0,
                end_char_idx=len(text)
            )]
            
    def _parse_resume_sections(self, text: str) -> List[DocumentSection]:
        # Common resume section headers (case insensitive)
        headers = [
            r"^summary", r"^professional summary", r"^objective", 
            r"^experience", r"^work experience", r"^employment history",
            r"^education", r"^academic background", 
            r"^skills", r"^core competencies", r"^technical skills",
            r"^projects", r"^personal projects",
            r"^certifications", r"^licenses",
            r"^achievements", r"^awards", r"^publications"
        ]
        return self._extract_sections(text, headers)
        
    def _parse_jd_sections(self, text: str) -> List[DocumentSection]:
        # Common JD section headers
        headers = [
            r"^overview", r"^about the role", r"^about us",
            r"^responsibilities", r"^what you'll do", r"^duties",
            r"^requirements", r"^qualifications", r"^minimum qualifications", r"^what we're looking for",
            r"^preferred qualifications", r"^nice to have",
            r"^skills", r"^technical skills",
            r"^benefits", r"^perks", r"^what we offer"
        ]
        return self._extract_sections(text, headers)
        
    def _extract_sections(self, text: str, header_patterns: List[str]) -> List[DocumentSection]:
        sections = []
        # Compile a single regex that matches any of the headers on a new line
        # Use multiline to match start of lines, allow some whitespace
        clean_patterns = [p.lstrip('^') for p in header_patterns]
        combined_pattern = r"(?im)^[\s]*(?:" + "|".join(clean_patterns) + r")[\s]*:?$"
        
        matches = list(re.finditer(combined_pattern, text))
        
        if not matches:
            # No sections found, treat as one big section
            return [DocumentSection(title="Overview", content=text, start_char_idx=0, end_char_idx=len(text))]
            
        # First chunk before any header (usually contact info / name in resumes)
        if matches[0].start() > 0:
            first_content = text[0:matches[0].start()].strip()
            if first_content:
                sections.append(DocumentSection(
                    title="Header",
                    content=first_content,
                    start_char_idx=0,
                    end_char_idx=matches[0].start()
                ))
                
        # Iterate over matches and extract content between them
        for i, match in enumerate(matches):
            title = match.group(0).strip().replace(':', '')
            start_idx = match.start()
            
            # Content ends at the start of the next match, or EOF
            end_idx = matches[i+1].start() if i + 1 < len(matches) else len(text)
            
            content = text[start_idx:end_idx].strip()
            sections.append(DocumentSection(
                title=title.title(),
                content=content,
                start_char_idx=start_idx,
                end_char_idx=end_idx
            ))
            
        return sections
