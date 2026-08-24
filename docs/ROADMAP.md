# Roadmap — CSA Assurance Planner

## Phase 0 — Documentation
- [x] README (EN + ES summary)
- [x] Regulatory references (FDA CSA, Part 820 themes, GPSV)
- [x] Glossary: intended use, process risk, assurance activity types
- [x] LICENSE · SECURITY.md · portfolio safety boundary

## Phase 1 — Core model
- [x] Assessment with intended use, GAMP category, and risk level
- [x] Requirement-level assurance items (scripted, unscripted, critical thinking, record, signature)
- [x] QA/CSV reviews with recorded decision
- [x] SQLite + synthetic seed examples

## Phase 2 — API & UI
- [x] FastAPI endpoints (`/health`, assessments, items, reviews, audit log)
- [x] React planner dashboard (summary, board, detail, new assessment, audit log)

## Phase 3 — Hardening
- [x] pytest + CI
- [x] Docker Compose (API + frontend)
- [x] CORS allowlist for local UI
- [ ] Authenticated identities / RBAC (production path, not this prototype)
- [ ] Coverage gate in CI

## Principle
Risk drives depth of assurance — documented explicitly, never implied as regulatory approval.
