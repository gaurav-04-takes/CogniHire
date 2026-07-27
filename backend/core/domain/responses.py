from pydantic import BaseModel, Field
from typing import List, Optional

class Recommendation(BaseModel):
    priority: str = Field(..., description="High, Medium, or Low")
    section: str = Field(..., description="Resume section affected, e.g., Summary, Skills, Experience")
    current_resume_evidence: str = Field(..., description="Current evidence from Resume")
    jd_requirement: str = Field(..., description="Requirement from JD")
    recommendation: str = Field(..., description="Recommended truthful change")
    rationale: str = Field(..., description="Reason the change matters")
    verification_required: bool = Field(..., description="Whether this change requires user verification")
    resume_citation_ids: List[str] = Field(default_factory=list, description="IDs of supporting Resume chunks")
    jd_citation_ids: List[str] = Field(default_factory=list, description="IDs of supporting JD chunks")

class SkillsAnalysis(BaseModel):
    present_and_supported: List[str] = Field(default_factory=list)
    present_but_underemphasized: List[str] = Field(default_factory=list)
    terminology_mismatch: List[str] = Field(default_factory=list)
    not_evidenced: List[str] = Field(default_factory=list)
    learning_recommendation: List[str] = Field(default_factory=list)

class ATSKeywords(BaseModel):
    safe_to_add_now: List[str] = Field(default_factory=list)
    add_only_if_accurate: List[str] = Field(default_factory=list)
    do_not_add_as_current_experience: List[str] = Field(default_factory=list)

class HonestGaps(BaseModel):
    resume_writing_gap: List[str] = Field(default_factory=list)
    terminology_gap: List[str] = Field(default_factory=list)
    evidence_gap: List[str] = Field(default_factory=list)
    actual_skill_gap: List[str] = Field(default_factory=list)
    experience_gap: List[str] = Field(default_factory=list)
    education_or_certification_gap: List[str] = Field(default_factory=list)

class NextActions(BaseModel):
    immediate_resume_changes: List[str] = Field(default_factory=list)
    verification_questions: List[str] = Field(default_factory=list)
    skills_to_learn: List[str] = Field(default_factory=list)
    projects_to_build: List[str] = Field(default_factory=list)
    interview_preparation_topics: List[str] = Field(default_factory=list)

class ResumeImprovementResponse(BaseModel):
    alignment_summary: str = Field(..., description="Brief assessment of Resume-JD alignment, strong matching areas, main gaps, important limitations")
    strengths: List[str] = Field(default_factory=list)
    high_priority_changes: List[Recommendation] = Field(default_factory=list)
    summary_recommendations: List[str] = Field(default_factory=list)
    skills_analysis: SkillsAnalysis
    experience_recommendations: List[Recommendation] = Field(default_factory=list)
    project_recommendations: List[Recommendation] = Field(default_factory=list)
    education_analysis: str = Field(...)
    certification_analysis: str = Field(...)
    ats_keywords: ATSKeywords
    section_order: List[str] = Field(default_factory=list)
    honest_gaps: HonestGaps
    next_actions: NextActions
    disclaimer: str = Field(default="These recommendations may improve alignment with the selected Job Description, but no resume change can guarantee ATS passage, an interview, or selection. Keep every statement accurate and verifiable.")
