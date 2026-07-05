-- Planning-grade PostgreSQL schema skeleton for the Honam/Gwangju official-source RAG MVP.
-- This file documents intended tables before production migration tooling is chosen.
-- pgvector: enable with `CREATE EXTENSION IF NOT EXISTS vector;` after confirming the target database supports it.
-- Privacy rule: do not store raw user questions. Store only representative, curated questions and non-identifying audit metadata.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TYPE source_status AS ENUM ('active', 'stale', 'retired');
CREATE TYPE reliability_tier AS ENUM ('official_primary', 'official_secondary', 'agency_referral');
CREATE TYPE supported_language AS ENUM ('ko', 'easy_ko', 'en', 'vi', 'zh');
CREATE TYPE audit_event_type AS ENUM (
  'health_check',
  'chat_refused',
  'chat_answered_with_citations',
  'empty_retrieval',
  'rate_limited',
  'provider_timeout',
  'provider_error'
);

CREATE TABLE official_sources (
  id BIGSERIAL PRIMARY KEY,
  source_name TEXT NOT NULL,
  source_url TEXT NOT NULL,
  jurisdiction TEXT NOT NULL DEFAULT 'Gwangju',
  language supported_language NOT NULL,
  topic TEXT NOT NULL,
  document_type TEXT NOT NULL,
  reliability reliability_tier NOT NULL,
  status source_status NOT NULL DEFAULT 'stale',
  source_hash TEXT,
  snapshot_id TEXT,
  checked_at TIMESTAMPTZ,
  update_policy TEXT NOT NULL,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT official_sources_snapshot_present CHECK (source_hash IS NOT NULL OR snapshot_id IS NOT NULL),
  CONSTRAINT official_sources_url_not_empty CHECK (length(trim(source_url)) > 0)
);

CREATE INDEX official_sources_status_idx ON official_sources (status);
CREATE INDEX official_sources_topic_idx ON official_sources (topic);
CREATE INDEX official_sources_language_idx ON official_sources (language);

CREATE TABLE source_chunks (
  id BIGSERIAL PRIMARY KEY,
  official_source_id BIGINT NOT NULL REFERENCES official_sources(id) ON DELETE CASCADE,
  chunk_key TEXT NOT NULL,
  quote_text TEXT NOT NULL,
  page_or_section TEXT NOT NULL,
  language supported_language NOT NULL,
  embedding_model TEXT,
  -- Vector dimension is a placeholder. Replace 1536 with the selected embedding model dimension after the model gate closes.
  embedding vector(1536),
  source_hash TEXT,
  snapshot_id TEXT,
  checked_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT source_chunks_snapshot_present CHECK (source_hash IS NOT NULL OR snapshot_id IS NOT NULL),
  CONSTRAINT source_chunks_quote_not_empty CHECK (length(trim(quote_text)) > 0),
  CONSTRAINT source_chunks_unique_key UNIQUE (official_source_id, chunk_key)
);

-- Add an ivfflat or hnsw index only after pgvector support, dimensions, and dataset size are confirmed.
-- Example after gate closure: CREATE INDEX source_chunks_embedding_idx ON source_chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX source_chunks_source_idx ON source_chunks (official_source_id);
CREATE INDEX source_chunks_language_idx ON source_chunks (language);

CREATE TABLE representative_questions (
  id BIGSERIAL PRIMARY KEY,
  question_key TEXT NOT NULL UNIQUE,
  language supported_language NOT NULL,
  topic TEXT NOT NULL,
  question_text TEXT NOT NULL,
  expected_behavior TEXT NOT NULL,
  safety_notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT representative_questions_text_not_empty CHECK (length(trim(question_text)) > 0)
);

CREATE TABLE representative_question_citations (
  representative_question_id BIGINT NOT NULL REFERENCES representative_questions(id) ON DELETE CASCADE,
  source_chunk_id BIGINT NOT NULL REFERENCES source_chunks(id) ON DELETE CASCADE,
  citation_purpose TEXT NOT NULL,
  PRIMARY KEY (representative_question_id, source_chunk_id)
);

CREATE TABLE institution_cards (
  id BIGSERIAL PRIMARY KEY,
  institution_name TEXT NOT NULL,
  jurisdiction TEXT NOT NULL DEFAULT 'Gwangju',
  topic TEXT NOT NULL,
  supported_languages supported_language[] NOT NULL DEFAULT ARRAY['ko']::supported_language[],
  official_url TEXT NOT NULL,
  phone TEXT,
  emergency BOOLEAN NOT NULL DEFAULT false,
  handoff_notes TEXT NOT NULL,
  source_id BIGINT REFERENCES official_sources(id) ON DELETE SET NULL,
  checked_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT institution_cards_url_not_empty CHECK (length(trim(official_url)) > 0)
);

CREATE INDEX institution_cards_topic_idx ON institution_cards (topic);
CREATE INDEX institution_cards_emergency_idx ON institution_cards (emergency);

CREATE TABLE audit_events (
  id BIGSERIAL PRIMARY KEY,
  event_type audit_event_type NOT NULL,
  occurred_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  request_language supported_language,
  response_status INTEGER,
  latency_ms INTEGER,
  retrieval_hit_count INTEGER,
  cited_source_ids BIGINT[] NOT NULL DEFAULT ARRAY[]::BIGINT[],
  refusal_reason TEXT,
  provider_name TEXT,
  error_code TEXT,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  -- Keep this table non-identifying: no raw question text, names, phone numbers, emails, IP addresses, or API keys.
  CONSTRAINT audit_events_latency_non_negative CHECK (latency_ms IS NULL OR latency_ms >= 0),
  CONSTRAINT audit_events_retrieval_hit_count_non_negative CHECK (retrieval_hit_count IS NULL OR retrieval_hit_count >= 0)
);

CREATE INDEX audit_events_type_time_idx ON audit_events (event_type, occurred_at DESC);
CREATE INDEX audit_events_language_idx ON audit_events (request_language);
