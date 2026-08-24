# Security Policy

## Supported versions

| Version | Support status |
|---|---|
| `0.2.x` | Current portfolio baseline; security fixes considered on a best-effort basis |
| `< 0.2` | Historical development snapshots; not supported |

This is a portfolio and learning project, not a hosted service or validated product. No service-level commitment is provided.

## Reporting a vulnerability

Do **not** open a public issue containing exploit details, credentials, personal data, confidential information, or regulated records.

Preferred reporting path:

1. Use GitHub private vulnerability reporting for this repository when the **Report a vulnerability** option is available under the Security tab.
2. If private reporting is unavailable, contact the maintainer through the LinkedIn profile linked in the README and request a private communication channel.

A useful report includes affected commit or endpoint, reproducible steps using **synthetic data only**, observed vs expected behavior, and confirmation that no real or regulated data was used.

## In-scope examples

- SQL injection or unsafe query construction
- bypass of actor attribution on write endpoints
- cross-site scripting in the planner UI
- leakage of repository or workflow secrets

## Out-of-scope examples

- missing production IAM, e-signatures, or Part 11 controls already documented as out of scope
- findings based on real employer, patient, or regulated data
- requests to certify the software as compliant or validated

## Secrets and data handling

- Never commit tokens, passwords, or real credentials.
- Use only synthetic records and fictional actors.
- Treat generated SQLite files as disposable demonstration data.
