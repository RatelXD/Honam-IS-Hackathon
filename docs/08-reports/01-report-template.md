---
title: Final Report Template
type: report-template
status: active
updated: 2026-07-08
owners:
  - project-maintainers
related:
  - ./90-appendix/05-evidence-ledger.md
  - ../00-overview/project-summary.md
  - ../01-requirements/req-official-source-rag.md
  - ../01-requirements/req-safety-privacy.md
---

# Final Report Template

## 1. Executive Summary

Summarize the Honam/Gwangju official source RAG MVP in one paragraph:

- target users: foreign residents and support operators
- core value: safe official-source guidance with citation and institution handoff
- implementation status: local feasibility MVP, not production-ready
- evidence anchor: tests, CI, docs, source inventory, and screenshots

## 2. Problem Background

Describe the information gap for foreign residents in the Honam region. Explain why unsupported chatbot answers can be harmful for immigration, health insurance, emergency, contract, and public-service questions.

## 3. Scope And Non-Goals

### In Scope

- web demo question input and language selection
- safety-first routing and refusal
- deterministic official-source seeded retrieval
- citation and institution card display
- docs-first governance and CI checks

### Out Of Scope For This MVP

- production deployment
- official partnership claims
- external LLM provider commitment
- storing raw user questions or personal data
- final legal, medical, immigration, or insurance eligibility judgments

## 4. Target Users And Representative Scenarios

Use representative scenarios from `docs/05-work-items/representative-questions.md`.

| Scenario | User need | Expected system behavior | Evidence |
| --- | --- | --- | --- |
| Settlement guidance | Find official institution and contact path | Answer with official citation and handoff | TBD |
| Source insufficient question | Ask for personal eligibility or judgment | Refuse final judgment and route to official institution | TBD |
| Emergency/sensitive question | Ask during danger or urgent health risk | Show emergency-first guidance before retrieval | TBD |

## 5. Official Source RAG Design

Explain the retrieval flow:

1. inspect safety and supported domain
2. search curated official-source snippets
3. validate citations against source URLs
4. compose a bounded answer
5. return institution cards and flags

Include source freshness fields when available: `source_url`, `checked_at`, `source_hash` or `snapshot_id`, `status`, and `citation_validation_result`.

## 6. Safety And Privacy

Summarize:

- no raw user question storage
- no fake citation
- refusal for unsupported personal judgment
- emergency-first handling for 112/119 scenarios
- provider/API keys are gated and not required for local seeded retrieval

## 7. Multilingual UX

Describe supported language intent and current UI behavior. Use multilingual glossary and representative question evidence when available. Keep claims limited to tested Korean, English, Vietnamese, and Chinese examples if those are the only verified paths.

## 8. System Architecture

Reference:

- `frontend/` for the Next.js UI
- `backend/` for FastAPI, safety, retrieval, and answer composition
- `database/` as planning schema only
- `docs/` as source of truth

Add a diagram or screenshot in the final draft when available.

## 9. Implementation Evidence Matrix

| Feature area | Status | Evidence link | Verification result | Notes |
| --- | --- | --- | --- | --- |
| Frontend chat UI | TBD | `frontend/app/page.tsx` | TBD | Include screenshot/build output. |
| Backend chat API | TBD | `backend/app/main.py` | TBD | Include pytest/API evidence. |
| Safety/refusal | TBD | `backend/app/safety.py` | TBD | Include refusal/emergency tests. |
| Retrieval/citation validation | TBD | `backend/app/retrieval.py` | TBD | Include source and citation tests. |
| Official source inventory | TBD | `docs/05-work-items/official-source-inventory.md` | TBD | Checked dates required before public claims. |
| Multilingual glossary | TBD | `docs/05-work-items/multilingual-glossary.md` | TBD | Tie glossary to UI evidence. |
| Deployment gate | Open | `docs/04-architecture/deployment-precheck.md` | TBD | Do not claim deployment until closed. |
| Docs/CI governance | In progress | `.github/workflows/ci.yml` | TBD | CI and pre-commit evidence required. |

## 10. Verification Results

List exact command logs and outcomes:

```text
backend: python -m pytest
frontend: npm ci, npm run frontend:lint, npm run --workspace frontend typecheck, npm run frontend:build
docs/security: pre-commit run --all-files
```

## 11. Limitations

Document current limitations plainly:

- not production-ready
- no official endorsement
- no real provider key commitment
- source freshness not complete until checked dates and validation rows exist
- deployment and database operation are gated

## 12. Future Work

Prioritize source verification, provider decision, deployment pre-check, accessibility review, and field feedback collection with synthetic/redacted evidence.

## 13. References

Use official/public links only. Include accessed or checked dates where possible.
