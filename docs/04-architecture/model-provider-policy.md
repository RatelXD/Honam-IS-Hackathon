# Model provider policy

This feasibility backend defaults to **disabled/local seeded retrieval**. The backend can rank curated official-source snippets and compose source-only guidance without calling an external model provider.

## Default behavior

- No external LLM call is required without keys.
- Product code must not call OpenAI, Gemini, or any other remote provider unless a pre-execution environment decision enables that provider.
- Seeded retrieval is deterministic and local: it uses checked official-source metadata already packaged with the backend.
- When sources are insufficient, the fallback is safe refusal/source-only guidance with institution handoff, not generated guesses.

## Provider priority

OpenAI/Gemini priority remains an environment and pre-execution decision, not an automatic runtime fallback. A deployment may choose a provider only after keys, safety checks, privacy review, and citation validation gates are explicitly satisfied.

Until that gate is opened, the provider order is:

1. Disabled/local seeded retrieval.
2. Safe refusal/source-only guidance when seeded sources do not cover the question.
3. No remote model provider.

## Safety boundary

The system must not infer personal visa, residence, legal, medical, insurance, or emergency judgments from short seed summaries. It may point to official institutions and verified URLs, and it must preserve the no-raw-question-persistence rule.
