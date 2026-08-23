from __future__ import annotations

import random
import string
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Header, HTTPException

from .database import get_connection
from .models import (
    AssessmentCreate,
    AssessmentOut,
    AssuranceItemCreate,
    AssuranceItemOut,
    ReviewCreate,
    ReviewOut,
    SummaryOut,
)

router = APIRouter()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _reference(prefix: str = "CSA") -> str:
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}-{suffix}"


def _audit(
    conn,
    actor: str,
    action: str,
    assessment_id: Optional[int] = None,
    detail: Optional[str] = None,
) -> None:
    conn.execute(
        "INSERT INTO audit_log (assessment_id, actor, action, detail, created_at) VALUES (?, ?, ?, ?, ?)",
        (assessment_id, actor, action, detail, _now()),
    )


def _require_assessment(conn, assessment_id: int) -> None:
    found = conn.execute(
        "SELECT 1 FROM assessments WHERE id = ?", (assessment_id,)
    ).fetchone()
    if not found:
        raise HTTPException(status_code=404, detail="Assessment not found")


@router.get("/summary", response_model=SummaryOut)
def summary() -> SummaryOut:
    conn = get_connection()
    try:
        total = conn.execute("SELECT COUNT(*) FROM assessments").fetchone()[0]
        high = conn.execute("SELECT COUNT(*) FROM assessments WHERE risk_level = 'high'").fetchone()[0]
        items = conn.execute("SELECT COUNT(*) FROM assurance_items").fetchone()[0]
        approved = conn.execute("SELECT COUNT(*) FROM reviews WHERE decision = 'approve'").fetchone()[0]
        return SummaryOut(
            total_assessments=total,
            high_risk_count=high,
            assurance_items=items,
            approved_reviews=approved,
        )
    finally:
        conn.close()


@router.get("/assessments", response_model=list[AssessmentOut])
def list_assessments(status: Optional[str] = None) -> list[dict]:
    conn = get_connection()
    try:
        if status:
            rows = conn.execute(
                "SELECT * FROM assessments WHERE status = ? ORDER BY id DESC", (status,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM assessments ORDER BY id DESC").fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


@router.post("/assessments", response_model=AssessmentOut, status_code=201)
def create_assessment(body: AssessmentCreate, x_actor: str = Header(...)) -> dict:
    conn = get_connection()
    assessment_ref = _reference()
    now = _now()
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO assessments
                (assessment_ref, title, system_name, gamp_category, intended_use, risk_level, status, created_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    assessment_ref, body.title, body.system_name, body.gamp_category,
                    body.intended_use, body.risk_level, "planned", body.created_by, now,
                ),
            )
            assessment_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            _audit(conn, x_actor, "assessment_created", assessment_id, f"ref={assessment_ref}")
        row = conn.execute("SELECT * FROM assessments WHERE id = ?", (assessment_id,)).fetchone()
        return dict(row)
    finally:
        conn.close()


@router.get("/assessments/{assessment_id}", response_model=AssessmentOut)
def get_assessment(assessment_id: int) -> dict:
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM assessments WHERE id = ?", (assessment_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Assessment not found")
        return dict(row)
    finally:
        conn.close()


@router.get("/assessments/{assessment_id}/items", response_model=list[AssuranceItemOut])
def list_items(assessment_id: int) -> list[dict]:
    conn = get_connection()
    try:
        _require_assessment(conn, assessment_id)
        rows = conn.execute(
            "SELECT * FROM assurance_items WHERE assessment_id = ? ORDER BY id",
            (assessment_id,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


@router.post("/assessments/{assessment_id}/items", response_model=AssuranceItemOut, status_code=201)
def add_item(assessment_id: int, body: AssuranceItemCreate, x_actor: str = Header(...)) -> dict:
    conn = get_connection()
    now = _now()
    try:
        _require_assessment(conn, assessment_id)
        with conn:
            conn.execute(
                """
                INSERT INTO assurance_items
                (assessment_id, requirement_ref, function_name, csa_class, rationale, test_strategy, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    assessment_id, body.requirement_ref, body.function_name, body.csa_class,
                    body.rationale, body.test_strategy, now,
                ),
            )
            item_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            _audit(
                conn, x_actor, "assurance_item_added", assessment_id,
                f"requirement={body.requirement_ref}; class={body.csa_class}",
            )
        row = conn.execute("SELECT * FROM assurance_items WHERE id = ?", (item_id,)).fetchone()
        return dict(row)
    finally:
        conn.close()


@router.get("/assessments/{assessment_id}/reviews", response_model=list[ReviewOut])
def list_reviews(assessment_id: int) -> list[dict]:
    conn = get_connection()
    try:
        _require_assessment(conn, assessment_id)
        rows = conn.execute(
            "SELECT * FROM reviews WHERE assessment_id = ? ORDER BY id DESC",
            (assessment_id,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


@router.post("/assessments/{assessment_id}/reviews", response_model=ReviewOut, status_code=201)
def add_review(assessment_id: int, body: ReviewCreate, x_actor: str = Header(...)) -> dict:
    conn = get_connection()
    now = _now()
    try:
        _require_assessment(conn, assessment_id)
        with conn:
            conn.execute(
                "INSERT INTO reviews (assessment_id, reviewer, decision, comment, reviewed_at) VALUES (?, ?, ?, ?, ?)",
                (assessment_id, body.reviewer, body.decision, body.comment, now),
            )
            review_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            _audit(conn, x_actor, "review_recorded", assessment_id, f"decision={body.decision}")
        row = conn.execute("SELECT * FROM reviews WHERE id = ?", (review_id,)).fetchone()
        return dict(row)
    finally:
        conn.close()


@router.get("/audit-log")
def audit_log(assessment_id: Optional[int] = None) -> list[dict]:
    conn = get_connection()
    try:
        if assessment_id is None:
            rows = conn.execute("SELECT * FROM audit_log ORDER BY id DESC LIMIT 200").fetchall()
        else:
            _require_assessment(conn, assessment_id)
            rows = conn.execute(
                "SELECT * FROM audit_log WHERE assessment_id = ? ORDER BY id DESC",
                (assessment_id,),
            ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
