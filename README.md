# CSA Assurance Planner

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-Vite-20232A?style=flat&logo=react&logoColor=61DAFB)
![Status](https://img.shields.io/badge/Status-Scaffold-orange?style=flat)

**Computer Software Assurance · FDA CSA · Risk-based testing · Production & QMS software**

*Portfolio-safe prototype — synthetic data only*

[Roadmap](docs/ROADMAP.md) · [Regulatory references](docs/REGULATORY_REFERENCES.md) · [Español](#español--resumen)

</div>

---

> **Data boundary:** All records are fictional. This is **not** validated software and must not be used to claim CSA compliance or release product.

---

## What this is

A planner that models **Computer Software Assurance (CSA)** thinking for software used in **production or quality management systems** (not product SaMD/SiMD):

1. **Intended use** — what the software does in the process  
2. **Risk** — impact on device quality / safety / record integrity if software fails  
3. **Assurance activities** — scripted tests, unscripted/exploratory approaches, vendor evidence (illustrative)  
4. **Assurance record** — lightweight evidence summary for learning purposes  

Aligned **conceptually** with FDA’s CSA guidance: scale rigor to risk instead of treating every tool the same.

**Stack (planned):** Python · FastAPI · Pydantic · SQLite · React · Docker · CI

---

## Why CSA matters now

FDA’s CSA guidance encourages a **risk-based** approach to establish confidence in automation used for production or QMS — complementary to classic CSV narratives and *General Principles of Software Validation*. Understanding CSA is increasingly expected in device and pharma IT/quality roles.

Sister projects:

| Project | Focus |
|---------|--------|
| [GxP Change Control](https://github.com/alianisreyesr/gxp-change-control) | Controlled change lifecycle |
| [CSV Evidence Tracker](https://github.com/alianisreyesr/csv-evidence-tracker) | RTM · IQ/OQ/PQ evidence patterns |
| [Quality Deviation Risk Monitor](https://github.com/alianisreyesr/quality-deviation-risk-monitor) | Deviation queue + audit trail |
| [Data Integrity Case File](https://github.com/alianisreyesr/data-integrity-case-file) | ALCOA+ investigations |

---

## Current status

| Area | Status |
|------|--------|
| Docs + FDA CSA map | ✅ |
| Risk taxonomy model | 🔜 |
| API + seed catalog of example systems | 🔜 |
| UI for assurance plans | 🔜 |
| Tests + Docker | 🔜 |

---

## Español — resumen

Planificador educativo de **Computer Software Assurance (CSA)** según la idea de la guía FDA: uso previsto → riesgo → actividades de assurance → registro. Solo datos sintéticos; no certifica cumplimiento.

---

**Built by [Alianis Reyes-Reyes](https://www.linkedin.com/in/alianis-reyes-reyes/)** · UPRM · Former Eli Lilly Intern
