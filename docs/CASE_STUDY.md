# Case study: risk-based software assurance planning

## Problem

Software assurance effort should follow intended use and risk instead of applying the same evidence depth to every requirement.

## Users and outcome

System owners document intended use, assurance practitioners classify requirements and activities, and quality reviewers inspect the rationale and history. The prototype produces a transparent plan rather than a black-box compliance score.

## Engineering decisions

- Explicit rule tables make assurance recommendations inspectable.
- FastAPI owns classification and lifecycle validation.
- React and TypeScript present the planning flow and maintain API contract clarity.
- Synthetic examples and SQLite support reproducible local demonstrations.

## Evidence

The project includes automated tests, CI, containerization, security guidance, architecture documentation, and an explicit production boundary.

## Boundary

The tool demonstrates CSA concepts but does not approve a system or replace an organization's risk management, quality procedures, validation evidence, or regulatory interpretation.
