# CSA Assurance Planner

<div align="center">

[![CI](https://github.com/alianisreyesr/csa-assurance-planner/actions/workflows/ci.yml/badge.svg)](https://github.com/alianisreyesr/csa-assurance-planner/actions/workflows/ci.yml)
[![CodeQL](https://github.com/alianisreyesr/csa-assurance-planner/actions/workflows/codeql.yml/badge.svg)](https://github.com/alianisreyesr/csa-assurance-planner/actions/workflows/codeql.yml)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?style=flat&logo=react&logoColor=black)
![SQLite](https://img.shields.io/badge/SQLite-evidence%20store-003B57?style=flat&logo=sqlite&logoColor=white)

**FDA CSA · Risk-Based Approach · Software Categorization · Assurance Planning · GxP**

*A portfolio-safe full-stack prototype for risk-proportionate software assurance planning*

[Screenshots](#portfolio-preview) · [Quick Start](#quick-start) · [Case study](docs/CASE_STUDY.md) · [CSA Alignment](docs/CSA_ALIGNMENT.md) · [Architecture](docs/architecture.md)

</div>

---

> **Data boundary:** All software systems and assurance plans are fictional/synthetic. This repository contains no proprietary, employer, patient, or regulated production data. It is **not validated software** and must not be used to make regulated quality decisions.

---

## Portfolio preview

| Assurance planning dashboard | Risk-based categorization |
|---|---|
| ![Synthetic CSA assurance planning dashboard](docs/assets/dashboard.png) | ![Synthetic risk-based software categorization](docs/assets/categorization.png) |

See the [case study](docs/CASE_STUDY.md) for the business problem, users, decisions, evidence, and production boundary.

## What This Is

CSA Assurance Planner models how a quality, IT compliance, or validation engineer translates the FDA Computer Software Assurance guidance into a structured, evidence-based workflow:

1. **Software intake** - Capture system name, intended use, GxP impact, and business criticality
2. **Risk-based categorization** - Determine software category (Category 1-3) based on intended use and GxP impact
3. **Assurance activity planning** - Generate proportionate testing and documentation activities based on category and risk
4. **Evidence capture** - Record testing decisions, rationale, and outcomes with attributable audit trail
5. **Assurance package** - Exportable summary of categorization rationale and planned/completed activities

**Stack:** Python 3.11 · FastAPI 0.115 · Pydantic v2 · SQLite · React 19 · Docker Compose · GitHub Actions

---

## CSA Alignment

The FDA 2022 CSA guidance emphasizes a risk-based, critical thinking approach over prescriptive validation documentation. This project operationalizes those principles:

| CSA Principle | Implementation |
|---|---|
| **Risk-proportionate assurance** | Category determines activity scope; low-risk systems require minimal documentation |
| **Intended use focus** | Categorization driven by patient safety and data integrity impact |
| **Critical thinking** | Planner requires explicit rationale for categorization decisions |
| **Leveraging supplier quality** | Category 1 (COTS) explicitly recognized with reduced testing burden |
| **Ongoing oversight** | Activity records and audit trail support periodic review |

See [docs/CSA_ALIGNMENT.md](docs/CSA_ALIGNMENT.md) for the full regulatory mapping.

---

## Quick Start

### Docker Compose - recommended

```bash
git clone https://github.com/alianisreyesr/csa-assurance-planner.git
cd csa-assurance-planner
docker compose up --build
```

Then open:
- Application: `http://localhost/`
- API health: `http://localhost/health`
- API docs: `http://localhost/docs`

### Local development

```bash
# Backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

---

## API Surface

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Service state + data boundary |
| `/summary` | GET | Portfolio-level assurance metrics |
| `/systems` | GET / POST | List or register software systems |
| `/systems/{id}` | GET | System detail |
| `/systems/{id}/categorize` | POST | Record risk-based categorization decision |
| `/systems/{id}/activities` | GET / POST | List or add assurance activities |
| `/systems/{id}/activities/{aid}` | PATCH | Update activity status or evidence |
| `/systems/{id}/assurance-package` | GET | Export categorization + activity summary |
| `/audit-log` | GET | Full attributable audit trail |

---

## Software Categories

| Category | Description | Assurance Approach |
|---|---|---|
| **Category 1** | Infrastructure / COTS used as-is | Supplier qualification focus; minimal additional testing |
| **Category 2** | Configured COTS / low GxP impact | Risk-based testing of configuration; reduced documentation |
| **Category 3** | Custom software / direct GxP impact | Full assurance lifecycle; test protocols, evidence, and rationale |

Categorization is recorded with explicit rationale, assessor identity, and UTC timestamp.

---

## Regulated Portfolio Ecosystem

| Project | Domain Focus | Status |
|---|---|---|
| **[Quality Deviation Risk Monitor](https://github.com/alianisreyesr/quality-deviation-risk-monitor)** | Deviation prioritization & explainable risk scoring | ✅ Active · 112 tests |
| **[CSV Evidence Tracker](https://github.com/alianisreyesr/csv-evidence-tracker)** | Requirements traceability, IQ/OQ/PQ test execution, audit trail | ✅ Active · 27 tests |
| **[GxP Change Control](https://github.com/alianisreyesr/gxp-change-control)** | Controlled change lifecycle & approvals | ✅ Active · 68 tests |
| **[Data Integrity Case File](https://github.com/alianisreyesr/data-integrity-case-file)** | ALCOA+ investigation, CAPA readiness, local AI triage | ✅ Active |
| **[GxP Batch Data Pipeline](https://github.com/alianisreyesr/gxp-batch-data-pipeline)** | Batch manufacturing pipeline — DuckDB · dbt · quality gates | ✅ Active · 12 tests |

---

<div align="center">

**Built by [Alianis Reyes-Reyes](https://www.linkedin.com/in/alianis-reyes-reyes/)**

Information Systems @ UPRM · Eli Lilly Tech@Lilly Alumni

*Assurance should be proportionate to risk - not to the thickness of the binder.*

</div>
