# Security Policy

## Supported Scope

This repository is a hackathon feasibility MVP. Security handling covers the code, docs, CI, issue templates, and local automation in this repository. It does not claim production deployment or operational incident response readiness.

## Do Not Disclose Secrets Publicly

Do not paste API keys, provider tokens, database URLs, private account details, raw user questions, personal data, or screenshots containing personal information into issues, pull requests, commit messages, docs, or demo evidence.

If a report requires sensitive details, first create a minimal public issue that says a private security report is needed, without including the secret itself. Share the sensitive detail only through a repository-private channel agreed by the maintainers.

## Reporting A Vulnerability

When reporting a security issue, include only non-sensitive information:

- affected area: `frontend`, `backend`, `database`, `docs`, `ci`, or `security`
- short impact summary
- reproduction steps using synthetic data
- expected behavior
- actual behavior
- whether official-source, citation, safety/refusal, or privacy behavior is affected

## Safety And Privacy Invariants

Security fixes must preserve these invariants:

- no raw user question or personal data storage
- no fake citations
- no committed secrets
- emergency-first handling remains visible
- unsupported legal, medical, immigration, insurance, labor, or housing judgments are refused or routed to official institutions

## Verification

Security-related PRs should run:

```bash
pre-commit run --all-files
cd backend && python -m pytest
cd .. && npm ci && npm run frontend:lint && npm run --workspace frontend typecheck && npm run frontend:build
```

Document any deferred security hardening in `docs/07-status/current-status.md`.
