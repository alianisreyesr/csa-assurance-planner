# Changelog

All notable changes to this portfolio project are documented in this file.

The project follows semantic versioning for public portfolio releases. Version numbers describe the repository's software baseline; they do not indicate regulatory validation, approval, or fitness for a regulated intended use.

## [Unreleased]

### Changed

- Version numbers aligned: API (`app/main.py`) and `frontend/package.json` now report 1.0.0, matching the changelog
- Runtime and dev requirements split and pinned; pytest/httpx no longer ship in the production image
- CI: ruff and mypy added, `pip-audit` pinned, least-privilege `permissions:`, coverage gate raised to 85 %, `npm ci` with the committed lockfile (also in `frontend/Dockerfile`)
- Fixed all ruff findings (import order, `X | None` annotations, `datetime.UTC`); added `ruff.toml`
- README: React 18 (not 19) and correct Docker Compose ports (UI 8080, API 8001); ROADMAP items marked complete

### Added

- Frontend unit tests (vitest) for the API client
- More complete `.gitignore`

### Fixed

- Recording a review now updates `assessments.status` (`approve` -> `approved`, `needs_revision` -> `needs_revision`) so the `?status=` filter reflects the review lifecycle
- CHANGELOG 1.0.0 entry described a different product (software categorization, exportable assurance package); rewritten to match the actual features
- API container now runs as a non-root user

## [1.0.0] — 2026-08-27

### Added

- Assessment intake capturing title, system name, GAMP category, intended use, and risk level (assessor's documented judgment)
- Advisory consistency notes (`app/rules.py`) that flag unusual GAMP category / risk level / CSA class combinations without blocking the assessor
- Assurance items per assessment with requirement reference, CSA class (record, signature, critical_thinking, unscripted, scripted), rationale, and test strategy
- Reviewer decisions (approve / needs_revision) with comments, and a summary endpoint
- Append-only audit log with a validated `X-Actor` header, action, and UTC timestamp
- FastAPI endpoints for assessments, items, reviews, summary, and audit log
- React + TypeScript reviewer interface and SQLite evidence store
- Dockerfile and Docker Compose (API + frontend)
- CI pipeline (pytest + coverage, pip-audit, Vite build) and CodeQL scanning

### Known limitations

- No authentication, role-based authorization, or electronic signatures
- SQLite is intended for local demonstration, not governed multi-user operation
- Synthetic data only; not validated software and must not be used for regulated quality decisions
