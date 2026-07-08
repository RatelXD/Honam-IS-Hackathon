---
title: Git Branch, Commit, And PR Convention
type: convention
status: active
updated: 2026-07-08
owners:
  - project-maintainers
applies_to:
  - frontend
  - backend
  - database
  - docs
  - ci
related:
  - ../02-decisions/adr-0001-docs-source-of-truth.md
  - ./conv-repo-structure.md
---

# Git Branch, Commit, And PR Convention

## Branches

Use feature branches. Do not commit directly to `main`.

Format:

```text
<type>/<slug>
```

Examples:

- `docs/repo-governance`
- `feat/rag-source-cards`
- `fix/backend-safety-refusal`
- `ci/pull-request-checks`

Allowed branch types: `feat`, `fix`, `docs`, `test`, `refactor`, `ci`, `chore`, `security`.

## Commits

Format:

```text
<type>(<scope>): <subject>
```

Examples:

- `docs(repo): restructure docs source taxonomy`
- `docs(report): add final report scaffold`
- `ci(repo): add pull request quality checks`
- `fix(backend): preserve emergency routing before retrieval`

Allowed commit types: `feat`, `fix`, `docs`, `test`, `refactor`, `ci`, `chore`, `build`, `security`.

Allowed scopes: `frontend`, `backend`, `database`, `rag`, `data`, `docs`, `ci`, `repo`, `report`, `security`.

Commit subjects must be imperative, reviewable, and specific. Do not use `wip`, `todo`, or `tbd` as the subject.

## Staging

Stage exact files. Do not use `git add .` for broad staging. Verify staged changes with:

```bash
git status --short
git diff --cached --stat
git diff --cached --check
```

## Pull Requests

Every PR must include:

- concise summary and linked issue when one exists
- docs impact
- verification commands and results
- source/citation impact when RAG or official-source behavior changes
- privacy/secret impact
- screenshots only when UI changed
- deployment/provider/database gate impact
- deferred items and known limitations

Docs and code should move together. If code changes behavior but docs do not change, the PR must explain why docs are unaffected.

## Git Identity

Before committing, ensure local identity is set and is not a placeholder automation identity:

```bash
git config user.name
git config user.email
```

Do not commit with empty values, `OpenAI Codex`, or `codex@openai.com`.

## Repository Settings Recommendation

GitHub branch protection should require PR review and the CI workflow once the team is ready. Local pre-commit hooks are recommended for parity, but GitHub Actions is the required PR gate.
