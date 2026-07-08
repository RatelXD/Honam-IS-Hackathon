---
title: Final Report Writing Convention
type: convention
status: active
updated: 2026-07-08
owners:
  - project-maintainers
applies_to:
  - report
  - docs
  - frontend
  - backend
  - rag
related:
  - ../08-reports/00-index.md
  - ../08-reports/01-report-template.md
  - ../08-reports/90-appendix/05-evidence-ledger.md
---

# Final Report Writing Convention

## Purpose

The final report must prove what the Honam IS Hackathon MVP actually implements. It should not read like a plan, a pitch deck, or a list of intentions. Every implementation claim needs evidence that a reviewer can trace to code, docs, tests, screenshots, command logs, source inventory rows, or PR/commit links.

## Writing Rules

- State the project as a Honam/Gwangju official source RAG feasibility MVP for foreign resident guidance.
- Separate implemented behavior, local demo behavior, planned behavior, and deferred decisions.
- Use official source and citation language precisely. Do not imply government endorsement.
- Explain safety and privacy boundaries before describing answer quality.
- Do not include raw user questions, personal data, real secrets, or private account details in examples.
- Mark unsupported domains as limitations instead of stretching the result.
- Keep screenshots and logs synthetic or redacted.

## Evidence Standard

A report claim is acceptable only when it points to at least one of these evidence types:

| Evidence type | Examples |
| --- | --- |
| Passing tests | `backend/tests/test_safety.py`, `backend/tests/test_retrieval.py`, pytest output |
| Frontend verification | lint, typecheck, build logs, screenshots of the local demo |
| API verification | `/health`, `/api/chat`, response shape checks, FastAPI tests |
| Source verification | official source inventory entries with URL, checked date, status, and citation validation result |
| Safety/privacy verification | refusal cases, emergency routing cases, no raw question storage review |
| Documentation evidence | ADRs, requirements, current status, service map, provider policy |
| Review evidence | PR checklist, commit hash, CI result, issue evidence table |

## Required Report Sections

1. Problem and target users
2. Scope and non-goals
3. Official source RAG design
4. Safety, refusal, and privacy policy
5. Multilingual UX and representative questions
6. System architecture
7. Implementation evidence matrix
8. Verification results
9. Limitations and deferred gates
10. Future work
11. References and appendix links

## Implementation Evidence Matrix

The report must include a feature-by-feature matrix. At minimum it must cover:

| Feature area | Required evidence |
| --- | --- |
| Frontend chat UI | Screenshot or build result plus source file links |
| Backend chat API | API contract and test result |
| Safety/refusal behavior | refusal and emergency-routing test evidence |
| Retrieval/citation validation | official source snippet tests and citation validation evidence |
| Official source inventory | inventory rows with checked dates or a clearly open verification gate |
| Multilingual glossary | glossary coverage and UX evidence |
| Deployment gate | deployment pre-check and status note |
| Docs/CI governance | PR template, CI workflow, pre-commit evidence |

## Limitations Language

Use direct limitation statements:

- "This MVP is not production-ready."
- "Provider selection is deferred until keys, costs, and privacy handling are documented."
- "Official source freshness requires checked dates and citation validation before public use."
- "The repository does not claim official partnership or endorsement."

Do not use ambiguous phrases such as "fully verified", "officially approved", or "production deployed" unless the evidence ledger proves them.
