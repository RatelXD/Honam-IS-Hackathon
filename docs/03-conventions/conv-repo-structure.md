---
title: Repository Structure Convention
type: convention
status: active
updated: 2026-07-08
owners:
  - project-maintainers
applies_to:
  - repo
  - frontend
  - backend
  - database
  - docs
related:
  - ../02-decisions/adr-0001-docs-source-of-truth.md
  - ./conv-git-branch-and-pr.md
---

# Repository Structure Convention

## Root Layout

The repository is a mono-repo for a feasibility MVP.

| Path | Responsibility |
| --- | --- |
| `frontend/` | Next.js TypeScript demo UI. Browser-exposed config only. |
| `backend/` | FastAPI API, safety, deterministic seeded retrieval, source validation. |
| `database/` | Planning-grade PostgreSQL/pgvector schema, not an applied production migration. |
| `docs/` | Source of truth for scope, requirements, decisions, architecture, work items, status, reports, and presentations. |
| `.github/` | Issue templates, PR template, CI, and repository workflow metadata. |
| `.env.example` | Variable names only. Never store real values. |
| `AGENTS.md` | Agent-facing project rules and command summary. |
| `README.md` | Human-facing quick start and project summary. |

## Docs Taxonomy

Docs use a numbered taxonomy modeled after `ChosunUniv2026Capstone/docs`, adapted inside this mono-repo's `docs/` root.

| Path | Purpose |
| --- | --- |
| `docs/00-overview/` | Project summary and context. |
| `docs/01-requirements/` | Functional, safety, privacy, language, and source requirements. |
| `docs/02-decisions/` | ADRs and accepted decisions. |
| `docs/03-conventions/` | Git, repo, reporting, and development conventions. |
| `docs/04-architecture/` | API contracts, MVP boundaries, provider policy, deployment pre-check, service map. |
| `docs/05-work-items/` | Source inventory, representative questions, role lanes, pre-execution gates, roadmap. |
| `docs/06-meetings/` | Meeting notes and digests once team collaboration starts. |
| `docs/07-status/` | Current status, risks, open questions, deferred enforcement. |
| `docs/08-reports/` | Final report, appendix, and evidence ledger. |
| `docs/09-ppts/` | Presentation plan and slide evidence checklist. |

Compatibility entrypoints may remain at old paths such as `docs/architecture/README.md` and `docs/planning/README.md`, but they must point to canonical numbered locations.

## Safety-Critical Ownership

Changes to these areas require docs review in the same PR:

- `backend/app/safety.py`
- `backend/app/retrieval.py`
- `backend/app/source_data.py`
- `backend/app/main.py` chat response construction
- `frontend/app/page.tsx` safety/refusal/citation rendering
- `docs/04-architecture/*`
- `docs/05-work-items/official-source-inventory.md`
- `docs/05-work-items/representative-questions.md`

## Forbidden Structure Drift

Do not add parallel source-of-truth files that conflict with numbered docs. Do not create new top-level app directories unless an ADR explains the boundary and README/AGENTS are updated.
