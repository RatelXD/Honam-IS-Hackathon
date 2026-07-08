---
title: Final Report Draft
type: report-draft
status: draft
updated: 2026-07-08
owners:
  - project-maintainers
related:
  - ../01-report-template.md
  - ../90-appendix/05-evidence-ledger.md
---

# Final Report Draft

## Executive Summary

Honam IS Hackathon is a local feasibility MVP for a Honam/Gwangju official source RAG web demo that helps foreign residents find administrative and daily-life guidance with safe refusal, citation display, and institution handoff. The current repository demonstrates the app structure and governance workflow, but it does not claim production readiness, official endorsement, or completed deployment.

## Problem And Target Users

Foreign residents often need public-service guidance across language and institution boundaries. Generic unsupported chatbot answers are risky when questions involve immigration, health insurance, emergencies, contracts, or personal eligibility. This MVP explores whether a constrained RAG workflow can answer only when official source evidence is available and route users to the right institution when the system should not make a final judgment.

Target users include foreign residents in the Honam region, newly arrived workers, international newcomers, family migrants, seasonal workers, and support operators preparing verified guidance.

## MVP Scope

Implemented or scaffolded areas should be reported with evidence only:

- frontend question input, language selection, answer display, citation display, institution cards, and fallback state
- backend health and chat API scaffold
- safety inspection and refusal behavior
- deterministic seeded retrieval and citation validation
- planning-grade database schema
- docs, PR templates, local hooks, and CI governance

Deferred areas:

- production deployment
- external provider selection
- operational database migration
- official partnership or endorsement
- real user-data collection

## Official Source RAG Design

The intended answer path is safety-first:

1. inspect whether the question is emergency/sensitive or unsupported
2. search only curated official-source snippets
3. validate source URLs and citation candidates
4. compose a bounded answer
5. return institution handoff and safety/provider flags

The final report must connect this description to backend tests, source inventory rows, and citation validation evidence.

## Safety And Privacy

The system should not store raw user questions or personal data in logs, issues, screenshots, or docs. It should refuse final legal, medical, insurance, immigration, and contract judgments when official-source evidence is insufficient. Emergency cases should prioritize 112 or 119 guidance before normal retrieval.

## Implementation Evidence Matrix

See [appendix evidence ledger](../90-appendix/05-evidence-ledger.md). Do not mark a row complete until the evidence link exists and the verification result is recorded.

## Verification Summary

| Gate | Result | Evidence |
| --- | --- | --- |
| Backend tests | TBD | TBD |
| Frontend lint/typecheck/build | TBD | TBD |
| Docs and secret checks | TBD | TBD |
| Source inventory freshness | Open | `docs/05-work-items/official-source-inventory.md` |
| Deployment readiness | Open | `docs/04-architecture/deployment-precheck.md` |

## Limitations

This MVP is not production-ready. It does not claim official endorsement, real deployment, complete source freshness, completed field feedback, or provider selection. Those items must stay visible as open gates until evidence closes them.

## Future Work

- verify official source inventory with checked dates and hashes
- decide provider policy with privacy/cost/fallback evidence
- complete deployment pre-check
- collect redacted or synthetic UX evidence
- expand multilingual evaluation scenarios
