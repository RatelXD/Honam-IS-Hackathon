# Repository Guidelines

## Project Overview

This repository is a personal feasibility MVP for a Honam/Gwangju official-source RAG web demo for foreign residents. The goal is to validate source-grounded administrative/life-support answers, safe refusals, emergency handoff, and multilingual responses. It is not production-ready: external LLM calls, deployment, production data collection, and operational migrations remain gated decisions.

Core rule: answer only from verified official sources. Do not invent citations, use blogs/community anecdotes as evidence, store raw user questions, or make final personal legal/medical/immigration/insurance judgments.

## Architecture & Data Flow

- `frontend/app/page.tsx` is a Next.js client demo. It reads `NEXT_PUBLIC_API_BASE_URL`, posts `{ question, language }` to `${API_BASE_URL}/api/chat`, and renders answers, citations, institution cards, emergency cards, and safety/provider flags. If no API base URL or the backend is unreachable, it shows a clearly labeled local fallback with no citation rows.
- `backend/app/main.py` exposes `GET /health` and `POST /api/chat`. Chat flow is safety-first: `inspect_question()` redacts/classifies input, `redacted_question` is used downstream, emergency/personal-sensitive branches return before retrieval, and ordinary responses require validated official snippets.
- Retrieval flow is deterministic and local: `search_snippets()` -> `validate_citation()` -> `compose_grounded_answer()` -> `ChatResponse`. Seed data lives in `backend/app/source_data.py`; product code should not fetch official URLs at request time.
- The planning database shape is PostgreSQL/pgvector in `database/schema.sql`, but it is a planning-grade skeleton, not an applied production migration.

## Key Directories

- `frontend/app/` - App Router UI entry points; currently a single public demo route plus root layout.
- `backend/app/` - FastAPI app, schemas, settings, safety classifier, seeded retrieval, and official-source seed data.
- `backend/tests/` - Pytest suites for API contract, safety/redaction, retrieval/citation validation, and health/settings behavior.
- `database/` - PostgreSQL/pgvector schema planning only.
- `docs/04-architecture/` - API contract, MVP boundaries, provider policy, and deployment precheck; keep these in sync with behavior changes.
- `docs/05-work-items/` - Source inventory, representative questions, glossary, and gate/checklist materials.

## Development Commands

Frontend from repo root:

```bash
npm install --workspace frontend
npm run frontend:dev
npm run frontend:build
npm run frontend:lint
npm run --workspace frontend typecheck
```

Backend from `backend/`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
uvicorn app.main:app --reload
python -m pytest
```

Focused backend tests:

```bash
cd backend
python -m pytest tests/test_chat.py::test_invalid_language_is_rejected
python -m pytest tests/test_safety.py tests/test_retrieval.py
```

Database planning command, only after DB/pgvector gates are confirmed:

```bash
psql "$DATABASE_URL" -f database/schema.sql
```

## Code Conventions & Common Patterns

- Python uses `from __future__ import annotations`, explicit typing, private helper functions with leading underscores, uppercase constants, and frozen dataclasses for internal safety/source objects.
- API boundaries are Pydantic models in `backend/app/schemas.py`; keep response fields stable for the frontend (`citations`, `institution_cards`, `emergency_cards`, `safety`).
- Safety and privacy are source-level invariants: preserve `raw_question_stored=false`, `raw_retention_days=0`, PII redaction, emergency-first routing, and refusal/handoff for personal judgments.
- Citation integrity is mandatory. Never return citations unless `validate_citation()` passes against official URL, metadata, source hash, and snapshot registry checks.
- Frontend TypeScript is strict. Keep API DTO fields snake_case to match backend JSON instead of translating to camelCase. State is managed with `useState`; derived selections use `useMemo`; styling is inline via `Record<string, CSSProperties>`.
- Frontend fallback mode must remain visibly labeled and must not fabricate live retrieval or citations. HTTP non-OK and JSON parse failures should be treated as errors, not citation-bearing fallbacks.
- Tests use pytest function tests, direct `assert`, FastAPI `TestClient`, pytest `monkeypatch`, and frozen dataclass fakes for API collaborators.

## Important Files

- `backend/app/main.py` - FastAPI entrypoint, CORS, `/health`, `/api/chat`, localized messages, response construction.
- `backend/app/schemas.py` - Request/response contract and allowed language enum: `ko`, `easy_ko`, `en`, `vi`, `zh`.
- `backend/app/safety.py` - PII redaction, emergency detection, and personal-judgment refusal logic.
- `backend/app/retrieval.py` - Deterministic keyword retrieval, citation validation, grounded answer composition, institution-card building.
- `backend/app/source_data.py` - Curated official-source snippets, URL allowlist, source hashes, snapshot registry.
- `backend/app/settings.py` - Runtime env defaults for provider mode, CORS origins, timeout/rate-limit knobs, RAG index path, and raw-retention days.
- `frontend/app/page.tsx` - Main demo UI, local fixtures, `/api/chat` fetch flow, fallback behavior, inline styles.
- `package.json`, `frontend/package.json`, `backend/pyproject.toml` - Canonical scripts, dependencies, Python version, pytest config.
- `.env.example` - Variable names only; never fill with real secrets.
- `docs/04-architecture/api-contract.md` - API shapes and safety/error code contract.

## Runtime/Tooling Preferences

- Package manager: npm workspaces with `package-lock.json`; `frontend` is the only npm workspace.
- Frontend stack: Next.js 14, React 18, TypeScript strict mode, React Strict Mode enabled.
- Backend stack: Python `>=3.11`, FastAPI, Uvicorn, pytest/httpx test extras.
- Public frontend env is limited to `NEXT_PUBLIC_API_BASE_URL`. Keep `OPENAI_API_KEY`, `GEMINI_API_KEY`, `DATABASE_URL`, and other secrets server-side only.
- Default model policy is disabled/local seeded retrieval. Do not add OpenAI, Gemini, or another remote provider path unless the documented provider/privacy/citation gates are explicitly opened.
- Deployment docs mention Vercel frontend and Render backend/PostgreSQL as candidates only; do not assume accounts, billing, CORS, pgvector, or migration readiness.

## Testing & QA

- Run backend tests from `backend/` so imports and relative doc checks match `backend/pyproject.toml` expectations.
- Core backend QA: health reports local seeded mode, no raw retention, no external LLM; `/api/chat` validates language, refuses unsupported sources, routes emergencies before retrieval, redacts PII, and returns citations only for validated official snippets.
- Retrieval QA must cover deterministic ranking, unsupported-domain empty results, official URL/hash/snapshot metadata, and localized source-insufficient messages.
- Safety QA must include positive and false-positive cases across Korean, English, Vietnamese, and Chinese, especially 112/119 emergencies, benign fireworks/police/fire-station queries, and personal visa/insurance/medical judgment refusals.
- Frontend QA should cover all five languages, configured vs unconfigured `NEXT_PUBLIC_API_BASE_URL`, fallback labeling, refusal banners, emergency-card ordering before answer text, and citation metadata rendering only when returned by the backend.
