"""
Rule-based document classification.

Architectural layer:
    Infrastructure.

Purpose:
    Implements a weighted keyword-based approach to determine if a document
    is a Resume or a Job Description.

Data flow:
    Takes raw document text from the ingestion pipeline and outputs a 
    ClassificationResult containing the likely type and confidence scores.

Key dependencies:
    - DocumentType, ClassificationResult domain models.

Related modules:
    - backend.core.interfaces.classifier
"""
import re
from backend.core.interfaces.classifier import IDocumentClassifier
from backend.core.domain.document import DocumentType, ClassificationResult

class RuleBasedDocumentClassifier(IDocumentClassifier):
    """
    Weighted keyword classifier for resumes and JDs.
    
    Belongs to the infrastructure layer and implements IDocumentClassifier.
    Calculates separate scores for Resume indicators and JD indicators, then
    compares them using confidence and margin thresholds.
    """
    def __init__(self, confidence_threshold: float = 2.0, margin_threshold: float = 1.0):
        self.confidence_threshold = confidence_threshold
        self.margin_threshold = margin_threshold
        
        # Strong indicators immediately signal the likely document type
        self.strong_resume = [
            "professional summary", "career objective", "work experience", 
            "employment history", "projects", "certifications", "contact details",
            "date ranges", "achievement"
        ]
        
        self.strong_jd = [
            "job description", "about the role", "responsibilities", 
            "required qualifications", "minimum qualifications", "preferred qualifications", 
            "what you will do", "what we are looking for", "benefits", 
            "equal opportunity employer", "apply now", "reports to", 
            "employment type", "salary range"
        ]
        
        # "Skills" appears frequently in both resumes and job descriptions, so the
        # term contributes only a weak score and cannot classify a document alone.
        self.weak_ambiguous = [
            "skills", "experience", "education", "qualifications", "technologies"
        ]

    def classify(self, text: str) -> ClassificationResult:
        """
        Classify text based on predefined keyword occurrence.

        Args:
            text: The normalized full text of the document.

        Returns:
            A ClassificationResult object. If the difference between scores
            (confidence) is too small, or the max score is below threshold,
            the result defaults to DocumentType.UNKNOWN.
            Ambiguous results remain UNKNOWN rather than defaulting to Resume. This
            prevents a JD from being indexed with Resume section rules.
        """
        text_lower = text.lower()
        
        matched_resume = []
        matched_jd = []
        matched_weak = []
        
        resume_score = 0.0
        jd_score = 0.0
        
        for kw in self.strong_resume:
            if kw in text_lower:
                matched_resume.append(kw)
                resume_score += 2.0
                
        for kw in self.strong_jd:
            if kw in text_lower:
                matched_jd.append(kw)
                jd_score += 2.0
                
        for kw in self.weak_ambiguous:
            if kw in text_lower:
                matched_weak.append(kw)
                # Weak indicators contribute very little to both or neither
                # We do not use them to sway the decision significantly
                resume_score += 0.1
                jd_score += 0.1
                
        # Additional heuristics (regex for dates, emails, etc.)
        if re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text_lower):
            matched_resume.append("email_address")
            resume_score += 1.0
            
        confidence = abs(resume_score - jd_score)
        
        if max(resume_score, jd_score) < self.confidence_threshold:
            doc_type = DocumentType.UNKNOWN
        elif confidence < self.margin_threshold:
            doc_type = DocumentType.UNKNOWN
        elif resume_score > jd_score:
            doc_type = DocumentType.RESUME
        else:
            doc_type = DocumentType.JOB_DESCRIPTION
            
        return ClassificationResult(
            document_type=doc_type,
            confidence=confidence,
            resume_score=resume_score,
            job_description_score=jd_score,
            matched_indicators={
                "resume": matched_resume,
                "job_description": matched_jd,
                "weak": matched_weak
            }
        )
