---
title: Safety And Privacy Requirements
type: requirement
status: active
updated: 2026-07-08
owners:
  - project-maintainers
related:
  - ../04-architecture/api-contract.md
  - ../04-architecture/mvp-boundaries.md
  - ../05-work-items/pre-execution-checklist.md
---

# Safety And Privacy Requirements

## Invariants

- Raw user questions are not stored.
- Raw question retention remains `0` days unless a future ADR changes it with privacy review.
- Secrets, API keys, provider keys, database URLs, passwords, and GitHub tokens are never committed.
- Emergency questions route to emergency guidance before retrieval.
- The system does not make final personal legal, medical, immigration, labor, insurance, or housing-contract judgments.
- Citations are never fabricated.

## Required Refusal Or Handoff Cases

The system must refuse or hand off when the user asks for:

- individual visa/work eligibility judgment
- individual health insurance fee correctness or entitlement judgment
- legal interpretation of a contract or dispute
- medical diagnosis or whether urgent care is unnecessary
- emergency or violence situations where 112/119 guidance should appear first
- any question not covered by current official-source snippets

## Evidence Rules

Verification evidence must avoid personal data. Use synthetic demo questions, redacted command output, public official-source URLs, and screenshots that do not expose private information.

## Deployment And Provider Safety

OpenAI, Gemini, database, Vercel, Render, and other provider/deployment choices remain gated until account, billing, secret storage, CORS, timeout, rate limit, failure behavior, and citation validation risks are documented.
