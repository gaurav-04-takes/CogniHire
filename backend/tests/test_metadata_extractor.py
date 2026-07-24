import pytest
from backend.core.domain.document import DocumentType
from backend.infrastructure.parsers.metadata_extractor import MetadataExtractor

def test_extract_resume_metadata_years_of_experience():
    extractor = MetadataExtractor()
    text = "John Doe\nSoftware Engineer\nI have 5 years of experience in Python."
    result = extractor.extract(text, DocumentType.RESUME)
    assert result.get("years_of_experience") == 5
    assert result.get("candidate_name") == "John Doe"

def test_extract_resume_metadata_education():
    extractor = MetadataExtractor()
    text = "Jane Doe\nEducation: Bachelor of Science"
    result = extractor.extract(text, DocumentType.RESUME)
    assert result.get("education_level") == "Bachelor"
    assert result.get("candidate_name") == "Jane Doe"

def test_extract_resume_metadata_no_match():
    extractor = MetadataExtractor()
    text = ""
    result = extractor.extract(text, DocumentType.RESUME)
    assert result == {}

def test_extract_jd_metadata():
    extractor = MetadataExtractor()
    text = "Senior Python Developer\nWe are looking for someone with 10+ years exp."
    result = extractor.extract(text, DocumentType.JOB_DESCRIPTION)
    assert result.get("required_years_of_experience") == 10
    assert result.get("job_title") == "Senior Python Developer"

def test_extract_jd_metadata_no_match():
    extractor = MetadataExtractor()
    text = ""
    result = extractor.extract(text, DocumentType.JOB_DESCRIPTION)
    assert result == {}

def test_extract_unknown_type():
    extractor = MetadataExtractor()
    text = "Some random text"
    result = extractor.extract(text, DocumentType.UNKNOWN)
    assert result == {}
