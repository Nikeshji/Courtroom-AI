from typing import List
from pydantic import BaseModel, Field

class CaseIntake(BaseModel):
    accused: str = Field(description="Name/description of accused person")
    victim: str = Field(description="Name/description of victim")
    offences: str = Field(description="Likely offences committed")
    allegation: str = Field(description="Core allegation in brief")
    jurisdiction: str = Field(description="Applicable jurisdiction")
    facts: List[str] = Field(default_factory=list, description="Material facts established")
    missing_information: List[str] = Field(default_factory=list, description="Information needed but not provided")

class ApplicableSection(BaseModel):
    section: str = Field(description="Section number/name")
    act: str = Field(description="Act name (BNS, BNSS, BSA)")
    relevance: str = Field(description="Why this applies")

class Precedent(BaseModel):
    case_name: str = Field(description="Name of case")
    court: str = Field(description="Which court decided it")
    year: str = Field(description="Year of decision")
    relevance: str = Field(description="Why it matters to this case")

class LegalResearch(BaseModel):
    applicable_sections: List[ApplicableSection] = Field(default_factory=list)
    precedents: List[Precedent] = Field(default_factory=list)
    evidentiary_notes: List[str] = Field(default_factory=list)
    unsettled_questions: List[str] = Field(default_factory=list)

class JudgeVerdict(BaseModel):
    verdict: str = Field(description="Guilty / Not Guilty / Partially Liable")
    confidence: int = Field(description="Confidence score 0-100", ge=0, le=100)
    findings: str = Field(description="Key findings of fact")
    prosecution_assessment: str = Field(description="Assessment of prosecution arguments")
    defense_assessment: str = Field(description="Assessment of defense arguments")
    reasoning: str = Field(description="Full legal reasoning")
    sections_applied: List[str] = Field(default_factory=list, description="Sections applied")
    probable_punishment: str = Field(description="Likely punishment if guilty")
