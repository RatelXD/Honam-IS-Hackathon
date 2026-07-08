---
title: Presentation Plan
type: presentation-plan
status: active
updated: 2026-07-08
owners:
  - project-maintainers
related:
  - ../08-reports/01-report-template.md
  - ../08-reports/90-appendix/05-evidence-ledger.md
---

# Presentation Plan

This folder tracks planned slide assets for the Honam/Gwangju official source RAG MVP. Do not store generated decks here until the team chooses a deck format.

## Storyline

| Slide | Purpose | Required evidence |
| --- | --- | --- |
| 1. Project title | Name the MVP and target region | Repo URL and project summary |
| 2. Problem | Foreign resident guidance gap | Problem statement and representative scenarios |
| 3. Safety-first approach | Explain refusal, emergency routing, and no raw question storage | Safety/privacy requirements |
| 4. Official source RAG flow | Show source-only retrieval and citation validation | Architecture/service map |
| 5. Demo UI | Show chat, citations, institution cards, fallback state | Screenshot or local demo capture |
| 6. Backend/API | Show `/health`, `/api/chat`, tests | API contract and pytest evidence |
| 7. Verification | Show CI, pre-commit, frontend build | CI and local command evidence |
| 8. Limitations | Open provider, deployment, source freshness gates | Current status and deployment pre-check |
| 9. Next steps | Source verification, provider decision, deployment gate, feedback | Roadmap and evidence ledger |

## Screenshot Checklist

- Landing/demo initial state with no personal data
- Official-source answer with citation card
- Source-insufficient refusal with institution handoff
- Emergency-first response for 112 or 119 scenario
- Multilingual label or response scenario if verified
- CI or terminal evidence with secrets redacted

## Asset Rules

- Use synthetic or redacted questions only.
- Do not include API keys, tokens, private account names, or personal contact details.
- Do not imply official endorsement.
- Match the final report status: local feasibility MVP unless deployment evidence exists.
