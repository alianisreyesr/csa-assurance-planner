# Changelog

All notable changes to this portfolio project are documented in this file.

The project follows semantic versioning for public portfolio releases. Version numbers describe the repository's software baseline; they do not indicate regulatory validation, approval, or fitness for a regulated intended use.

## [1.0.0] — 2026-08-27

### Added

- Software intake capturing system name, intended use, GxP impact, and business criticality
- Risk-based categorization (Category 1–3) aligned to FDA Computer Software Assurance guidance
- Proportionate assurance-activity planning generated from category and risk
- Evidence capture with attributable actor and audit trail
- Exportable assurance package summarizing categorization rationale and activities
- FastAPI endpoints for systems, categorization, activities, and audit log
- React reviewer interface and SQLite evidence store
- Dockerfile and Docker Compose (API + frontend)
- CI pipeline (pytest + coverage, pip-audit, Vite build) and CodeQL scanning

### Known limitations

- No authentication, role-based authorization, or electronic signatures
- SQLite is intended for local demonstration, not governed multi-user operation
- Synthetic data only; not validated software and must not be used for regulated quality decisions
