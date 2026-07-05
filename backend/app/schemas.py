"""Pydantic schemas for the backend API boundary."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, HttpUrl


class SupportedLanguage(StrEnum):
    ko = "ko"
    easy_ko = "easy_ko"
    en = "en"
    vi = "vi"
    zh = "zh"


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2_000)
    language: SupportedLanguage = SupportedLanguage.ko


class SourceCitation(BaseModel):
    title: str
    url: HttpUrl
    institution: str
    retrieved_at: str | None = None
    excerpt: str | None = None
    source_hash: str | None = None
    snapshot_id: str | None = None
    page_or_section: str | None = None


class InstitutionCard(BaseModel):
    name: str
    description: str
    phone: str | None = None
    url: HttpUrl | None = None
    address: str | None = None
    reason: str | None = None


class EmergencyCard(BaseModel):
    type: str
    phone: str
    priority: int = 0
    message: str


class SafetyMetadata(BaseModel):
    is_refusal: bool
    code: str
    detected_categories: list[str] = Field(default_factory=list)
    redacted_question: str = ""
    raw_question_stored: bool = False
    raw_retention_days: int = 0
    scaffold_only: bool = False
    external_llm_enabled: bool = False
    provider_disabled: bool = True
    guidance: list[str] = Field(default_factory=list)


class ChatResponse(BaseModel):
    answer: str
    language: SupportedLanguage
    citations: list[SourceCitation] = Field(default_factory=list)
    institution_cards: list[InstitutionCard] = Field(default_factory=list)
    emergency_cards: list[EmergencyCard] = Field(default_factory=list)
    safety: SafetyMetadata
