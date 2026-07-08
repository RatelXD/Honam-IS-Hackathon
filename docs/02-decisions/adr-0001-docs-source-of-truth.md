---
title: ADR-0001 Docs As Repository Source Of Truth
type: decision
status: accepted
date: 2026-07-08
updated: 2026-07-08
owners:
  - project-maintainers
related:
  - ../00-overview/project-summary.md
  - ../03-conventions/conv-git-branch-and-pr.md
  - ../03-conventions/conv-repo-structure.md
---

# ADR-0001 Docs As Repository Source Of Truth

## Context

This repository is a hackathon feasibility MVP with frontend, backend, database planning, source policy, deployment gates, and report artifacts in one repository. Safety and source-grounding rules can drift if they live only in code comments, issues, or chat history.

## Decision

The `docs/` directory is the repository source of truth for product scope, safety/privacy policy, architecture boundaries, official-source RAG assumptions, provider/deployment gates, work items, status, and reports.

Behavior-changing work must update the relevant docs before or with the code change when it affects:

- supported regions, languages, topics, or user-facing scope
- source inventory, citation validation, or RAG behavior
- privacy, raw question retention, emergency routing, or refusal rules
- provider, database, deployment, CORS, timeout, retry, or rate-limit assumptions
- final report claims, evidence, screenshots, or demo scenarios

## Consequences

- A PR can be rejected for missing docs when behavior, safety, or deployment assumptions changed.
- README and AGENTS summarize the current repo, but canonical details live under numbered `docs/` sections.
- Old entrypoints such as `docs/architecture/README.md` and `docs/planning/README.md` only redirect readers to canonical locations.
- Completion claims must cite code, tests, command output, screenshots, source inventory entries, or PR/commit evidence.
