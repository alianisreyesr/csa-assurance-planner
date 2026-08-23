from typing import Literal, Optional
from pydantic import BaseModel, Field

GampCategory = Literal["1", "3", "4", "5"]
RiskLevel = Literal["low", "medium", "high"]
CsaClass = Literal["record", "signature", "critical_thinking", "unscripted", "scripted"]
ReviewDecision = Literal["approve", "needs_revision"]


class AssessmentCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    system_name: str = Field(..., min_length=2, max_length=100)
    gamp_category: GampCategory
    intended_use: str = Field(..., min_length=10, max_length=500)
    risk_level: RiskLevel
    created_by: str = Field(..., min_length=2, max_length=80)


class AssessmentOut(BaseModel):
    id: int
    assessment_ref: str
    title: str
    system_name: str
    gamp_category: str
    intended_use: str
    risk_level: str
    status: str
    created_by: str
    created_at: str


class AssuranceItemCreate(BaseModel):
    requirement_ref: str = Field(..., min_length=2, max_length=40)
    function_name: str = Field(..., min_length=3, max_length=200)
    csa_class: CsaClass
    rationale: str = Field(..., min_length=10, max_length=500)
    test_strategy: str = Field(..., min_length=10, max_length=500)


class AssuranceItemOut(BaseModel):
    id: int
    assessment_id: int
    requirement_ref: str
    function_name: str
    csa_class: str
    rationale: str
    test_strategy: str
    created_at: str


class ReviewCreate(BaseModel):
    reviewer: str = Field(..., min_length=2, max_length=80)
    decision: ReviewDecision
    comment: Optional[str] = Field(None, max_length=500)


class ReviewOut(BaseModel):
    id: int
    assessment_id: int
    reviewer: str
    decision: str
    comment: Optional[str]
    reviewed_at: str


class SummaryOut(BaseModel):
    total_assessments: int
    high_risk_count: int
    assurance_items: int
    approved_reviews: int
    data_boundary: str = "All records are synthetic and fictional."
