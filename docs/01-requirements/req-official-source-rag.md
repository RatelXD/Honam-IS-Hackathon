---
title: Official-Source RAG Requirements
type: requirement
status: active
updated: 2026-07-08
owners:
  - project-maintainers
related:
  - ../05-work-items/official-source-inventory.md
  - ../05-work-items/representative-questions.md
  - ../04-architecture/api-contract.md
---

# Official-Source RAG Requirements

## Goal

The system must answer administrative and daily-life questions only when it has verified official-source evidence or a safe institution handoff.

## Functional Requirements

- The frontend must collect a user question and supported language value.
- The backend must validate request shape and supported language.
- Retrieval must use curated official-source snippets packaged with or explicitly approved by the project.
- Answers must include citations only when citation validation passes.
- Institution and emergency cards must be available when the safest action is handoff.
- Unsupported or source-insufficient questions must produce refusal/source-limitation responses rather than guesses.
- Representative questions in `docs/05-work-items/representative-questions.md` define demo scenarios and expected behavior.

## Source Requirements

Every source candidate must track:

- official URL or official institution reference
- source name and jurisdiction
- language
- topic
- checked date or timestamp
- source hash or snapshot identifier when the source is ingested
- status: `active`, `stale`, or `retired`
- reliability tier and update policy

## Non-Goals

- No private community scraping.
- No blog, anecdote, or personal experience as answer evidence.
- No production claim that the demo replaces immigration office, medical, legal, labor, or insurance experts.
- No real-time crawling at request time in the MVP.
