"""Runtime settings for the backend scaffold.

Only environment variable names are encoded here. Secret values must stay in local or
platform secret stores and are not required for the scaffold endpoints.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


SUPPORTED_LLM_PROVIDERS = {"disabled", "openai", "gemini"}


def _get_int(name: str, default: int, *, minimum: int | None = None) -> int:
    raw_value = os.getenv(name)
    if raw_value is None or raw_value.strip() == "":
        return default

    try:
        value = int(raw_value)
    except ValueError:
        return default

    if minimum is not None and value < minimum:
        return minimum
    return value


def _get_csv(name: str, default: tuple[str, ...]) -> tuple[str, ...]:
    raw_value = os.getenv(name)
    if raw_value is None or raw_value.strip() == "":
        return default

    values = tuple(item.strip() for item in raw_value.split(",") if item.strip())
    return values or default


@dataclass(frozen=True)
class Settings:
    llm_provider: str
    allowed_origins: tuple[str, ...]
    request_timeout_ms: int
    rate_limit_window_ms: int
    rate_limit_max_requests: int
    raw_retention_days: int
    rag_index_path: str

    @property
    def scaffold_only(self) -> bool:
        """Hard true until G003 wires and verifies real retrieval/generation.

        Provider and index environment variables can be present for deployment
        pre-checks, but they must not imply product readiness while this scaffold
        still returns refusal-only responses.
        """
        return True


def get_settings() -> Settings:
    provider = os.getenv("LLM_PROVIDER", "disabled").strip().lower() or "disabled"
    if provider not in SUPPORTED_LLM_PROVIDERS:
        provider = "disabled"

    return Settings(
        llm_provider=provider,
        allowed_origins=_get_csv("ALLOWED_ORIGINS", ("http://localhost:3000",)),
        request_timeout_ms=_get_int("REQUEST_TIMEOUT_MS", 30_000, minimum=1),
        rate_limit_window_ms=_get_int("RATE_LIMIT_WINDOW_MS", 60_000, minimum=1),
        rate_limit_max_requests=_get_int("RATE_LIMIT_MAX_REQUESTS", 60, minimum=1),
        raw_retention_days=_get_int("RAW_RETENTION_DAYS", 0, minimum=0),
        rag_index_path=os.getenv("RAG_INDEX_PATH", "").strip(),
    )
