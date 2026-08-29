"""Populate the local SQLite database with synthetic CSA planning records."""
from __future__ import annotations

import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import get_connection, init_db
from app.utils import now, reference

random.seed(7)


ASSESSMENTS = [
    (
        "LIMS audit trail review strategy",
        "LIMS-01",
        "4",
        "Define a risk-based assurance approach for the audit trail review workflow.",
        "high",
        "A.Reyes",
    ),
    (
        "eBR exception handling verification scope",
        "EBR-02",
        "5",
        "Map critical-thinking and scripted tests for electronic batch record exception paths.",
        "high",
        "J.Torres",
    ),
    (
        "QMS training evidence assessment",
        "QMS-03",
        "3",
        "Plan right-sized testing for a training evidence workflow after a controlled change.",
        "medium",
        "M.Colon",
    ),
    (
        "Backup restore evidence planning",
        "INFRA-04",
        "1",
        "Determine proportionate assurance evidence for backup restore checks.",
        "low",
        "L.Rivera",
    ),
]

ITEMS = [
    (
        "REQ-001",
        "Audit trail capture",
        "critical_thinking",
        "The function affects attributable, contemporaneous traceability of critical actions.",
        "Challenge actor capture, UTC timestamps, and before-and-after value persistence.",
    ),
    (
        "REQ-002",
        "Electronic signature enforcement",
        "scripted",
        "A failed signature must block completion of a controlled record.",
        "Execute positive and negative scripted signature scenarios with expected outcomes.",
    ),
    (
        "REQ-003",
        "Exception workflow branching",
        "unscripted",
        "Branch behavior depends on contextual reviewer judgment and exception conditions.",
        "Use exploratory scenarios to challenge exception routing and incomplete evidence.",
    ),
]

REVIEWS = [
    ("QualityReviewer1", "approve", "Risk-based approach is proportionate to the intended use."),
    ("CSVLead", "needs_revision", "Expand challenge coverage for exception-handling edge cases."),
]


def seed() -> None:
    init_db()
    conn = get_connection()
    try:
        with conn:
            existing = conn.execute("SELECT COUNT(*) FROM assessments").fetchone()[0]
            if existing:
                print("Database already contains records; seed skipped.")
                return

            assessment_ids: list[int] = []
            for index, data in enumerate(ASSESSMENTS):
                assessment_ref = reference()
                conn.execute(
                    """
                    INSERT INTO assessments
                    (assessment_ref, title, system_name, gamp_category, intended_use, risk_level, status, created_by, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    # data = (title, system_name, gamp_category, intended_use,
                    # risk_level, created_by) — "planned" (status) must be
                    # inserted before created_by, matching the column list
                    # above. Splicing it in after *data unpacked put
                    # created_by's value into the status column and
                    # "planned" into created_by.
                    (assessment_ref, *data[:5], "planned", data[5], now(20 - index * 3)),
                )
                assessment_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                assessment_ids.append(assessment_id)
                conn.execute(
                    "INSERT INTO audit_log (assessment_id, actor, action, detail, created_at) VALUES (?, ?, ?, ?, ?)",
                    (assessment_id, "seed_script", "assessment_seeded", f"ref={assessment_ref}", now(20 - index * 3)),
                )

            for assessment_id in assessment_ids[:3]:
                for requirement_ref, function_name, csa_class, rationale, strategy in ITEMS:
                    conn.execute(
                        """
                        INSERT INTO assurance_items
                        (assessment_id, requirement_ref, function_name, csa_class, rationale, test_strategy, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (assessment_id, requirement_ref, function_name, csa_class, rationale, strategy, now(10)),
                    )
                    conn.execute(
                        "INSERT INTO audit_log (assessment_id, actor, action, detail, created_at) VALUES (?, ?, ?, ?, ?)",
                        (assessment_id, "seed_script", "assurance_item_seeded", f"requirement={requirement_ref}", now(10)),
                    )

            for assessment_id in assessment_ids[:2]:
                for reviewer, decision, comment in REVIEWS:
                    conn.execute(
                        "INSERT INTO reviews (assessment_id, reviewer, decision, comment, reviewed_at) VALUES (?, ?, ?, ?, ?)",
                        (assessment_id, reviewer, decision, comment, now(5)),
                    )
                    conn.execute(
                        "INSERT INTO audit_log (assessment_id, actor, action, detail, created_at) VALUES (?, ?, ?, ?, ?)",
                        (assessment_id, reviewer, "review_seeded", f"decision={decision}", now(5)),
                    )
    finally:
        conn.close()

    print("Seeded 4 synthetic assessments, 9 assurance items, and 4 reviews.")


if __name__ == "__main__":
    seed()
