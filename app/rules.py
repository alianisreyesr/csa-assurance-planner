"""Explainable, non-blocking consistency checks for CSA planning records.

These are deliberately advisory, not a rejection gate: FDA CSA guidance is
risk-based and intended-use-driven, not a rigid lookup table from GAMP
category to risk level or from risk level to test rigor — a real assessor's
judgment can validly override any of these. What *would* misrepresent the
guidance is pretending a fixed mapping exists and using it to reject an
assessment outright. So this module only surfaces flags for a human
reviewer to weigh, computed fresh on every read rather than trusted from
client input.
"""
from __future__ import annotations

from fastapi import HTTPException

# Roughly increasing rigor, per FDA CSA's "unscripted testing where
# justified by risk, scripted/signature verification where not" framing.
# Used only to flag the single combination worth a second look — a
# high-risk item relying solely on the lowest-rigor class — not to rank
# or gate every combination.
_LOWEST_RIGOR_CLASS = "unscripted"


def assessment_consistency_notes(gamp_category: str, risk_level: str) -> list[str]:
    """Flag the one broadly-accepted GAMP 5 heuristic worth surfacing:
    Category 5 (custom/bespoke) software carries the highest inherent risk
    profile of any GAMP category, so pairing it with risk_level=low is
    unusual enough to deserve a documented reason.
    """
    notes: list[str] = []
    if gamp_category == "5" and risk_level == "low":
        notes.append(
            "GAMP Category 5 (custom/bespoke) software is typically not "
            "assessed as low risk — confirm the intended use genuinely "
            "has no direct GxP impact, or document why."
        )
    return notes


def item_consistency_notes(assessment_risk_level: str, csa_class: str) -> list[str]:
    """Flag a high-risk assessment whose assurance item relies solely on
    unscripted testing, per CSA's expectation that assurance rigor scale
    with risk — not a rejection, just a prompt to document the rationale.
    """
    notes: list[str] = []
    if assessment_risk_level == "high" and csa_class == _LOWEST_RIGOR_CLASS:
        notes.append(
            "High-risk assessment paired with unscripted testing — confirm "
            "the rationale documents why unscripted coverage is sufficient "
            "for this requirement."
        )
    return notes


def clean_actor(x_actor: str) -> str:
    """Validate the X-Actor header the same way created_by/reviewer fields
    are validated, instead of writing an unbounded, unvalidated string
    straight into the audit trail."""
    value = x_actor.strip()
    if not (2 <= len(value) <= 80):
        raise HTTPException(
            status_code=422,
            detail="X-Actor header must be 2-80 characters after trimming.",
        )
    return value
