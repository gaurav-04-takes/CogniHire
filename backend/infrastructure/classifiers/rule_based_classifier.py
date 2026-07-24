import re
from backend.core.interfaces.classifier import IDocumentClassifier
from backend.core.domain.document import DocumentType, ClassificationResult

class RuleBasedDocumentClassifier(IDocumentClassifier):
    def __init__(self, confidence_threshold: float = 2.0, margin_threshold: float = 1.0):
        self.confidence_threshold = confidence_threshold
        self.margin_threshold = margin_threshold
        
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
        
        self.weak_ambiguous = [
            "skills", "experience", "education", "qualifications", "technologies"
        ]

    def classify(self, text: str) -> ClassificationResult:
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
