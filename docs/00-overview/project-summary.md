---
title: Project Summary
type: overview
status: active
updated: 2026-07-08
owners:
  - project-maintainers
related:
  - ../01-requirements/req-official-source-rag.md
  - ../01-requirements/req-safety-privacy.md
  - ../04-architecture/mvp-boundaries.md
  - ../05-work-items/official-source-inventory.md
---

# Project Summary

## One-Line Summary

Honam IS Hackathon is a feasibility MVP for a Honam/Gwangju official-source RAG web demo that helps foreign residents find administrative and daily-life guidance with safe refusal and institution handoff.

## Target Users

- foreign residents in the Honam region
- newly arrived foreign workers
- international students
- marriage migrants and family members
- seasonal workers
- support-center or PM/docs operators preparing verified guidance

## Problem

Foreign residents often need local administrative and daily-life information across language, institution, and source boundaries. Generic translation or unsupported chatbot answers can be unsafe when the topic involves immigration, health insurance, emergency help, contracts, medical symptoms, or legal judgment.

## MVP Value

The MVP validates whether a small web demo can:

- accept a question in a supported language
- route emergencies before retrieval
- refuse unsupported personal judgments
- answer only from curated official-source snippets
- show citations, institution cards, and safety/provider flags
- avoid storing raw user questions or personal data

## Current Repository Shape

| Area | Current role |
| --- | --- |
| `frontend/` | Next.js TypeScript demo UI for question input, language selection, answers, citations, institution cards, emergency cards, and fallback state. |
| `backend/` | FastAPI app with `/health`, `/api/chat`, safety inspection, deterministic retrieval, citation validation, and grounded answer composition. |
| `database/` | Planning-grade PostgreSQL/pgvector schema for future source/chunk/question data. |
| `docs/` | Source of truth for scope, requirements, architecture, work items, status, reports, and presentations. |

## Current Status

The repository is not production-ready. External LLM calls, deployment, production data collection, operational database migrations, real provider keys, and official partnership claims remain gated decisions.

Baseline for the governance rollout: `41a28e26035b3af3147ee443a1999d917efb20db` (`Tighten retrieval domain gating`).
