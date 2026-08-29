import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import init_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_database(tmp_path, monkeypatch):
    path = str(tmp_path / "test.db")
    monkeypatch.setenv("DB_PATH", path)
    import app.database as database

    database.DB_PATH = path
    init_db()
    yield


def assessment_payload():
    return {
        "title": "LIMS audit trail assurance plan",
        "system_name": "LIMS-TEST",
        "gamp_category": "4",
        "intended_use": "Plan risk-based assurance for an audit trail review workflow.",
        "risk_level": "high",
        "created_by": "tester",
    }


def create_assessment():
    response = client.post(
        "/assessments",
        json=assessment_payload(),
        headers={"x-actor": "tester"},
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_and_get_assessment():
    assessment_id = create_assessment()
    response = client.get(f"/assessments/{assessment_id}")
    assert response.status_code == 200
    assert response.json()["risk_level"] == "high"


def test_create_assessment_requires_actor_header():
    response = client.post("/assessments", json=assessment_payload())
    assert response.status_code == 422


def test_add_and_list_assurance_item():
    assessment_id = create_assessment()
    item = {
        "requirement_ref": "REQ-001",
        "function_name": "Audit trail capture",
        "csa_class": "critical_thinking",
        "rationale": "This function affects attributable traceability of critical records.",
        "test_strategy": "Challenge actor capture, timestamps, and before-and-after values.",
    }
    response = client.post(
        f"/assessments/{assessment_id}/items",
        json=item,
        headers={"x-actor": "tester"},
    )
    assert response.status_code == 201
    listed = client.get(f"/assessments/{assessment_id}/items")
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_add_review_and_audit_entry():
    assessment_id = create_assessment()
    response = client.post(
        f"/assessments/{assessment_id}/reviews",
        json={"reviewer": "qa_reviewer", "decision": "approve", "comment": "Proportionate."},
        headers={"x-actor": "qa_reviewer"},
    )
    assert response.status_code == 201
    audit = client.get(f"/audit-log?assessment_id={assessment_id}")
    assert audit.status_code == 200
    assert len(audit.json()) >= 2


def test_summary_reflects_assessment():
    create_assessment()
    response = client.get("/summary")
    assert response.status_code == 200
    assert response.json()["total_assessments"] == 1
    assert response.json()["high_risk_count"] == 1


def test_missing_assessment_returns_404():
    response = client.get("/assessments/99999")
    assert response.status_code == 404


def test_category_5_low_risk_gets_consistency_note():
    payload = assessment_payload()
    payload["gamp_category"] = "5"
    payload["risk_level"] = "low"
    response = client.post("/assessments", json=payload, headers={"x-actor": "tester"})
    assert response.status_code == 201
    notes = response.json()["consistency_notes"]
    assert any("Category 5" in n for n in notes)


def test_typical_category_risk_combo_has_no_note():
    assessment_id = create_assessment()  # category 4 / high — unremarkable
    response = client.get(f"/assessments/{assessment_id}")
    assert response.json()["consistency_notes"] == []


def test_high_risk_unscripted_item_gets_consistency_note():
    assessment_id = create_assessment()  # risk_level=high
    item = {
        "requirement_ref": "REQ-002",
        "function_name": "Exception routing",
        "csa_class": "unscripted",
        "rationale": "Exploratory coverage based on reviewer judgment.",
        "test_strategy": "Ad hoc exploratory testing.",
    }
    response = client.post(
        f"/assessments/{assessment_id}/items", json=item, headers={"x-actor": "tester"}
    )
    assert response.status_code == 201
    notes = response.json()["consistency_notes"]
    assert any("unscripted" in n for n in notes)


def test_actor_header_must_be_within_length_bounds():
    response = client.post("/assessments", json=assessment_payload(), headers={"x-actor": "a"})
    assert response.status_code == 422

    response = client.post(
        "/assessments", json=assessment_payload(), headers={"x-actor": "x" * 200}
    )
    assert response.status_code == 422
