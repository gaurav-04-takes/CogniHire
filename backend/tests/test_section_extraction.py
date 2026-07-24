import pytest
from backend.infrastructure.parsers.section_parser import RuleBasedSectionParser
from backend.core.domain.document import DocumentType

def test_resume_section_extraction():
    parser = RuleBasedSectionParser()
    text = "John Doe\nExperience\nWorked at Apple.\nEducation\nBS CS."
    sections = parser.parse_sections(text, DocumentType.RESUME)
    
    assert len(sections) == 3
    assert sections[0].title == "Header"
    assert sections[1].title == "Experience"
    assert "Worked at Apple." in sections[1].content
    assert sections[2].title == "Education"
    assert "BS CS." in sections[2].content

def test_jd_section_extraction():
    parser = RuleBasedSectionParser()
    text = "Company X\nResponsibilities\nDo things.\nRequirements\nKnow things."
    sections = parser.parse_sections(text, DocumentType.JOB_DESCRIPTION)
    
    assert len(sections) == 3
    assert sections[0].title == "Header"
    assert sections[1].title == "Responsibilities"
    assert sections[2].title == "Requirements"
