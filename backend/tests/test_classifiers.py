import pytest
from backend.infrastructure.classifiers.rule_based_classifier import RuleBasedDocumentClassifier
from backend.core.domain.document import DocumentType

def test_resume_detection():
    classifier = RuleBasedDocumentClassifier()
    resume_text = "John Doe\nProfessional Summary\nSoftware Engineer\nWork Experience\n- 5 years at Google\nEducation\nB.S. Computer Science\nContact details: 555-1234"
    res = classifier.classify(resume_text)
    assert res.document_type == DocumentType.RESUME
    assert res.resume_score > res.job_description_score

def test_jd_detection():
    classifier = RuleBasedDocumentClassifier()
    jd_text = "About the Role\nWe are looking for a Software Engineer.\nResponsibilities\n- Write code\nRequired Qualifications\n- 5 years of experience\nEmployment type: Full-time"
    res = classifier.classify(jd_text)
    assert res.document_type == DocumentType.JOB_DESCRIPTION
    assert res.job_description_score > res.resume_score

def test_jd_with_weak_resume_indicators():
    classifier = RuleBasedDocumentClassifier()
    # JD with weak indicators like "skills", "experience", "education"
    jd_text = "Job Description\nResponsibilities: Write code.\nRequired Skills\nMust have 5 years experience\nEducation: Bachelor's degree\nSalary range: $100k-$120k"
    res = classifier.classify(jd_text)
    # The weak indicators (skills, experience, education) contribute slightly but strong JD indicators should win
    assert res.document_type == DocumentType.JOB_DESCRIPTION

def test_ambiguous_detection_defaults_to_unknown():
    classifier = RuleBasedDocumentClassifier()
    ambiguous_text = "Hello world this is just some text with skills and experience but nothing strong."
    res = classifier.classify(ambiguous_text)
    # Falls back to UNKNOWN now
    assert res.document_type == DocumentType.UNKNOWN
