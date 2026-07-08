---
title: Service Map
type: architecture
status: active
updated: 2026-07-08
owners:
  - project-maintainers
related:
  - ./mvp-boundaries.md
  - ./api-contract.md
  - ./model-provider-policy.md
  - ./deployment-precheck.md
---

# Service Map

## Runtime Shape

```text
Next.js frontend -> FastAPI backend -> safety inspector -> seeded retrieval -> citation validation -> grounded response
```

## Components

| Component | Path | Current responsibility | Gate / limitation |
| --- | --- | --- | --- |
| Frontend | `frontend/app/page.tsx` | Demo UI, language selection, API call, fallback display, answer/citation/institution/emergency rendering. | Browser QA and visual polish remain future hardening. |
| Backend API | `backend/app/main.py` | `/health`, `/api/chat`, request validation, response assembly, localized messages. | External provider calls remain disabled/gated. |
| Safety | `backend/app/safety.py` | PII redaction, emergency detection, personal-judgment classification. | Must stay before retrieval. |
| Retrieval | `backend/app/retrieval.py` | Deterministic local search and citation validation. | Seeded local retrieval only until provider/source gates close. |
| Source data | `backend/app/source_data.py` | Curated official-source snippets, allowlist, hashes, snapshot registry. | Must not fetch arbitrary URLs at request time. |
| Settings | `backend/app/settings.py` | Provider mode, CORS, timeout/rate-limit knobs, retention defaults. | Secrets must stay outside repo. |
| Database planning | `database/schema.sql` | PostgreSQL/pgvector planning schema. | Not an applied production migration. |
| Docs | `docs/` | Source of truth for requirements, decisions, architecture, work items, status, reports. | Must be updated with behavior/safety/source changes. |

## Data And Privacy Flow

1. User submits a question and language.
2. Backend validates and inspects the question.
3. Safety routing can return before retrieval.
4. Retrieval only uses local official-source seed data.
5. Citation validation must pass before citations are returned.
6. Raw user question is not persisted.

## Future Candidate Services

Future deployment may split frontend, backend, and database across Vercel, Render, and PostgreSQL only after the deployment pre-check is closed. Until then, the app remains a local feasibility MVP.
