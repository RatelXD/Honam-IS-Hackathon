# Contributing

This repository is a hackathon feasibility MVP for a Honam/Gwangju official-source RAG demo. Contributions should keep the current safety-first scope intact: official sources only, no raw question storage, no fake citations, no secrets, and no production-readiness claims without evidence.

## Workflow

1. Create a feature branch from `origin/main`.
2. Follow the branch format in `docs/03-conventions/conv-git-branch-and-pr.md`.
3. Keep changes focused and stage exact files.
4. Update docs before or with behavior, safety, source, provider, database, deployment, or report changes.
5. Open a PR using `.github/pull_request_template.md` once verification passes.

## Commit Messages

Use:

```text
<type>(<scope>): <subject>
```

Examples:

- `docs(repo): define collaboration conventions`
- `ci(repo): add pull request quality checks`
- `fix(backend): preserve refusal for personal visa judgments`

Allowed types and scopes are documented in `docs/03-conventions/conv-git-branch-and-pr.md`.

## Local Verification

Run the checks relevant to your change. For a full local gate:

```bash
git diff --check
cd backend
python -m pytest
cd ..
npm install --workspace frontend
npm run frontend:lint
npm run --workspace frontend typecheck
npm run frontend:build
```

Docs-only changes should at minimum run `git diff --check` and the docs link checker described in the repository PR template.

## Optional Local Hooks

Local pre-commit is recommended for parity with CI, but GitHub Actions is the required PR gate.

```bash
python -m pip install pre-commit gitlint
pre-commit install --hook-type pre-commit --hook-type commit-msg
pre-commit run --all-files
```

## Privacy And Secret Rules

Never commit:

- API keys, GitHub tokens, provider keys, database URLs, or passwords
- raw user questions or screenshots/logs containing personal data
- team member phone numbers, private emails, signatures, or account credentials
- unsupported claims that the app gives final legal, medical, immigration, labor, or insurance judgments

If evidence is needed, use redacted command output, public official-source URLs, synthetic demo questions, or screenshots that do not expose personal data.

## Pull Request Expectations

A PR should state:

- what changed
- why it changed
- docs impact
- verification commands and results
- safety/privacy/source/citation impact
- deployment/provider/database gate impact
- known limitations or deferred work
