---
title: Evidence Ledger
type: report-appendix
status: active
updated: 2026-07-08
owners:
  - project-maintainers
related:
  - ../01-report-template.md
  - ../../05-work-items/representative-questions.md
  - ../../05-work-items/official-source-inventory.md
---

# Evidence Ledger

Use this ledger to connect final-report claims to reviewable evidence. Do not paste raw user questions, secrets, or personal data. Use synthetic, representative, or redacted examples.

## Feature Evidence Matrix

| Feature area | Claim status | Evidence source | Verification command or review | Result | Notes |
| --- | --- | --- | --- | --- | --- |
| Frontend chat UI | Needs final evidence | `frontend/app/page.tsx` | `npm run frontend:lint`, `npm run --workspace frontend typecheck`, `npm run frontend:build`, screenshot review | TBD | Include answer, citation, institution card, emergency, and fallback states. |
| Backend chat API | Needs final evidence | `backend/app/main.py`, `backend/tests/test_chat.py` | `python -m pytest` | TBD | Verify response shape and safety/provider flags. |
| Safety/refusal | Needs final evidence | `backend/app/safety.py`, `backend/tests/test_safety.py` | `python -m pytest backend/tests/test_safety.py` | TBD | Cover source-insufficient refusal and emergency-first routing. |
| Retrieval/citation validation | Needs final evidence | `backend/app/retrieval.py`, `backend/app/source_data.py`, `backend/tests/test_retrieval.py` | `python -m pytest backend/tests/test_retrieval.py` | TBD | Citation must trace to official source snippets. |
| Official source inventory | Open gate | `docs/05-work-items/official-source-inventory.md` | Source URL, checked date, status, hash/snapshot review | TBD | Do not claim freshness until rows are verified. |
| Multilingual glossary | Needs final evidence | `docs/05-work-items/multilingual-glossary.md` | Glossary review plus UI scenario evidence | TBD | Tie Korean, English, Vietnamese, and Chinese labels to tested UI behavior. |
| Deployment gate | Open gate | `docs/04-architecture/deployment-precheck.md` | Deployment checklist review | TBD | No production deployment claim until closed. |
| Docs/CI governance | Needs final evidence | `.github/workflows/ci.yml`, `.pre-commit-config.yaml`, `.gitlint` | CI/pre-commit/gitlint evidence | TBD | Required PR gate is GitHub Actions; local hooks are parity. |

## Representative Question Evidence

| Question ID | Scenario type | Expected official source | Expected behavior | Evidence link | Citation validation result |
| --- | --- | --- | --- | --- | --- |
| Q01 | normal_rag | HiKorea/Ministry of Justice, 1345 | Official-source summary and institution handoff | TBD | TBD |
| Q03 | normal_rag | National Health Insurance Service | Bounded guidance and official inquiry path | TBD | TBD |
| Q07 | source_insufficient_refusal | HiKorea/Ministry of Justice, 1345 | Refuse final personal work eligibility judgment | TBD | TBD |
| Q11 | emergency_sensitive_routing | 112, 119 | Emergency-first guidance | TBD | TBD |
| Q14 | emergency_sensitive_routing | 119 | Emergency-first guidance, no medical diagnosis | TBD | TBD |

## Command Evidence Log

| Date | Gate | Command | Result | Artifact |
| --- | --- | --- | --- | --- |
| 2026-07-08 | Governance taxonomy | markdown link check | Passed | `.omo/evidence/task-2-link-check.txt` |
| 2026-07-08 | Local hooks | `pre-commit run --all-files` | Passed | `.omo/evidence/task-6-pre-commit.txt` |
| 2026-07-08 | CI parity | backend/frontend/pre-commit local equivalents | Passed | `.omo/evidence/task-7-local-ci.txt` |

## Evidence Quality Checklist

- Evidence is reproducible from the repository or linked PR/commit.
- Screenshots avoid raw user questions and personal data.
- Source claims include official URL and checked date where applicable.
- Unsupported or deferred work is marked open, not silently omitted.
- Final report language matches `docs/07-status/current-status.md`.
