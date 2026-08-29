from __future__ import annotations

import sqlite3
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException

from .database import get_db
from .models import (
    AssessmentCreate,
    AssessmentOut,
    AssuranceItemCreate,
    AssuranceItemOut,
    ReviewCreate,
    ReviewOut,
    SummaryOut,
)
from .rules import assessment_consistency_notes, clean_actor, item_consistency_notes
from .utils import now as _now
from .utils import reference as _reference

router = APIRouter()


def _audit(
    conn: sqlite3.Connection,
    actor: str,
    action: str,
    assessment_id: Optional[int] = None,
    detail: Optional[str] = None,
) -> None:
    conn.execute(
        "INSERT INTO audit_log (assessment_id, actor, action, detail, created_at) VALUES (?, ?, ?, ?, ?)",
        (assessment_id, actor, action, detail, _now()),
    )


def _require_assessment(conn: sqlite3.Connection, assessment_id: int) -> sqlite3.Row:
    row = conn.execute(
        "SELECT * FROM assessments WHERE id = ?", (assessment_id,)
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return row


def _serialize_assessment(row: sqlite3.Row) -> dict:
    data = dict(row)
    data["consistency_notes"] = assessment_consistency_notes(
        data["gamp_category"], data["risk_level"]
    )
    return data


def _serialize_item(row: sqlite3.Row, assessment_risk_level: str) -> dict:
    data = dict(row)
    data["consistency_notes"] = item_consistency_notes(assessment_risk_level, data["csa_class"])
    return data


@router.get("/summary", response_model=SummaryOut)
def summary(conn: sqlite3.Connection = Depends(get_db)) -> SummaryOut:
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


@router.get("/assessments", response_model=list[AssessmentOut])
def list_assessments(
    status: Optional[str] = None,
    conn: sqlite3.Connection = Depends(get_db),
) -> list[dict]:
    if status:
        rows = conn.execute(
            "SELECT * FROM assessments WHERE status = ? ORDER BY id DESC", (status,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM assessments ORDER BY id DESC").fetchall()
    return [_serialize_assessment(row) for row in rows]


@router.post("/assessments", response_model=AssessmentOut, status_code=201)
def create_assessment(
    body: AssessmentCreate,
    x_actor: str = Header(...),
    conn: sqlite3.Connection = Depends(get_db),
) -> dict:
    actor = clean_actor(x_actor)
    assessment_ref = _reference()
    now = _now()
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
        _audit(conn, actor, "assessment_created", assessment_id, f"ref={assessment_ref}")
    row = conn.execute("SELECT * FROM assessments WHERE id = ?", (assessment_id,)).fetchone()
    return _serialize_assessment(row)


@router.get("/assessments/{assessment_id}", response_model=AssessmentOut)
def get_assessment(assessment_id: int, conn: sqlite3.Connection = Depends(get_db)) -> dict:
    row = _require_assessment(conn, assessment_id)
    return _serialize_assessment(row)


@router.get("/assessments/{assessment_id}/items", response_model=list[AssuranceItemOut])
def list_items(assessment_id: int, conn: sqlite3.Connection = Depends(get_db)) -> list[dict]:
    assessment = _require_assessment(conn, assessment_id)
    rows = conn.execute(
        "SELECT * FROM assurance_items WHERE assessment_id = ? ORDER BY id",
        (assessment_id,),
    ).fetchall()
    return [_serialize_item(row, assessment["risk_level"]) for row in rows]


@router.post("/assessments/{assessment_id}/items", response_model=AssuranceItemOut, status_code=201)
def add_item(
    assessment_id: int,
    body: AssuranceItemCreate,
    x_actor: str = Header(...),
    conn: sqlite3.Connection = Depends(get_db),
) -> dict:
    actor = clean_actor(x_actor)
    assessment = _require_assessment(conn, assessment_id)
    now = _now()
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
            conn, actor, "assurance_item_added", assessment_id,
            f"requirement={body.requirement_ref}; class={body.csa_class}",
        )
    row = conn.execute("SELECT * FROM assurance_items WHERE id = ?", (item_id,)).fetchone()
    return _serialize_item(row, assessment["risk_level"])


@router.get("/assessments/{assessment_id}/reviews", response_model=list[ReviewOut])
def list_reviews(assessment_id: int, conn: sqlite3.Connection = Depends(get_db)) -> list[dict]:
    _require_assessment(conn, assessment_id)
    rows = conn.execute(
        "SELECT * FROM reviews WHERE assessment_id = ? ORDER BY id DESC",
        (assessment_id,),
    ).fetchall()
    return [dict(row) for row in rows]


@router.post("/assessments/{assessment_id}/reviews", response_model=ReviewOut, status_code=201)
def add_review(
    assessment_id: int,
    body: ReviewCreate,
    x_actor: str = Header(...),
    conn: sqlite3.Connection = Depends(get_db),
) -> dict:
    actor = clean_actor(x_actor)
    _require_assessment(conn, assessment_id)
    now = _now()
    with conn:
        conn.execute(
            "INSERT INTO reviews (assessment_id, reviewer, decision, comment, reviewed_at) VALUES (?, ?, ?, ?, ?)",
            (assessment_id, body.reviewer, body.decision, body.comment, now),
        )
        review_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        _audit(conn, actor, "review_recorded", assessment_id, f"decision={body.decision}")
    row = conn.execute("SELECT * FROM reviews WHERE id = ?", (review_id,)).fetchone()
    return dict(row)


@router.get("/audit-log")
def audit_log(
    assessment_id: Optional[int] = None,
    conn: sqlite3.Connection = Depends(get_db),
) -> list[dict]:
    if assessment_id is None:
        rows = conn.execute("SELECT * FROM audit_log ORDER BY id DESC LIMIT 200").fetchall()
    else:
        _require_assessment(conn, assessment_id)
        rows = conn.execute(
            "SELECT * FROM audit_log WHERE assessment_id = ? ORDER BY id DESC",
            (assessment_id,),
        ).fetchall()
    return [dict(row) for row in rows]
