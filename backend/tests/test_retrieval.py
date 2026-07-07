from pathlib import Path

import pytest

from app.retrieval import (
    build_institution_cards,
    compose_grounded_answer,
    search_snippets,
    validate_citation,
)
from app.source_data import (
    OFFICIAL_SOURCE_URLS,
    SEEDED_SOURCE_SNIPPETS,
    SNAPSHOT_HASH_REGISTRY,
    SourceSnippet,
    _seed_source_hash,
)


def test_keyword_retrieval_is_deterministic_and_ranks_immigration_1345_first() -> None:
    first = search_snippets("비자 체류 상담 1345", limit=3)
    second = search_snippets("비자 체류 상담 1345", limit=3)

    assert first == second
    assert [snippet.id for snippet in first][:2] == [
        "immigration-1345-contact-center",
        "hikorea-portal-main",
    ]


def test_seed_snippets_use_official_urls_and_real_citation_metadata() -> None:
    assert {snippet.source_url for snippet in SEEDED_SOURCE_SNIPPETS} == OFFICIAL_SOURCE_URLS

    for snippet in SEEDED_SOURCE_SNIPPETS:
        assert validate_citation(snippet)
        assert snippet.id
        assert snippet.source_name
        assert snippet.title
        assert snippet.institution
        assert snippet.checked_at == "2026-07-03"
        assert snippet.page_or_section
        assert snippet.quote_text
        assert snippet.keywords
        assert snippet.supported_languages
        assert snippet.source_hash == _seed_source_hash(
            snippet.source_url,
            snippet.checked_at,
            snippet.page_or_section,
            snippet.quote_text,
        )
        assert SNAPSHOT_HASH_REGISTRY[snippet.snapshot_id] == snippet.source_hash
        assert "example.com" not in snippet.source_url
        assert "TODO" not in snippet.quote_text


def test_citation_validation_fails_for_incomplete_snippet() -> None:
    incomplete = SourceSnippet(
        id="incomplete",
        source_name="HiKorea",
        title="Missing required citation metadata",
        source_url="https://www.hikorea.go.kr/Main.pt",
        institution="Korea Immigration Service / Ministry of Justice",
        topic="immigration_portal",
        checked_at="2026-07-03",
        page_or_section="",
        quote_text="Official portal guidance.",
        keywords=("visa",),
        supported_languages=("en",),
        source_hash=None,
        snapshot_id=None,
    )

    assert validate_citation(incomplete) is False


def test_multilingual_answer_stays_grounded_and_avoids_final_judgment() -> None:
    snippets = search_snippets("건강보험 외국인 가입 자격", limit=2)

    answer = compose_grounded_answer("건강보험 가입 가능해?", "vi", snippets)

    assert "không đưa ra kết luận cuối cùng" in answer
    assert "https://www.nhis.or.kr/english/wbheaa02900m01.do" in answer
    assert "Bạn đủ điều kiện" not in answer
    assert "eligible" not in answer.lower()


def test_institution_cards_are_built_from_valid_official_snippets_only() -> None:
    snippets = search_snippets("119 ambulance emergency", limit=2)

    cards = build_institution_cards(snippets)

    assert cards[0]["name"] == "National Fire Agency 119"
    assert cards[0]["phone"] == "119"
    assert cards[0]["url"] == "https://www.nfa.go.kr/nfa/safetyinfo/emergencyservice/119emergencydeclaration/"
    assert all(card["url"] in OFFICIAL_SOURCE_URLS for card in cards)


def test_provider_policy_doc_presence_and_required_policy_terms() -> None:
    policy = Path("../docs/architecture/model-provider-policy.md").read_text(encoding="utf-8")

    assert "disabled/local seeded retrieval" in policy
    assert "OpenAI" in policy
    assert "Gemini" in policy
    assert "No external LLM call is required without keys" in policy
    assert "safe refusal/source-only guidance" in policy

def test_broad_gwangju_query_without_supported_domain_returns_no_snippets() -> None:
    assert search_snippets("광주에서 가장 맛있는 식당을 추천해줘") == []


@pytest.mark.parametrize(
    "query",
    [
        "Where can I stay at a hotel near Gwangju Station?",
        "Please recommend lodging for my travel stay in Gwangju.",
        "Is there official tourism guidance on where visitors should stay overnight?",
    ],
)
def test_lodging_and_travel_stay_queries_do_not_retrieve_immigration_sources(query: str) -> None:
    assert search_snippets(query, limit=3) == []


@pytest.mark.parametrize(
    ("query", "expected_topic"),
    [
        ("How can foreign residents check status of stay guidance?", "immigration_portal"),
        ("Where can I check stay guidance from official sources?", "immigration_portal"),
        ("외국인 체류 상담 1345", "immigration_hotline"),
        ("Tôi cần tư vấn nhập cư", "immigration_hotline"),
        ("外国人医疗保险在哪里确认", "health_insurance"),
        ("119 ambulance emergency", "fire_medical_emergency"),
        ("health insurance for foreign residents", "health_insurance"),
    ],
)
def test_supported_official_source_domains_still_retrieve_expected_snippets(
    query: str,
    expected_topic: str,
) -> None:
    snippets = search_snippets(query, limit=3)

    assert snippets, query
    assert any(snippet.topic == expected_topic for snippet in snippets), [
        snippet.id for snippet in snippets
    ]

def test_chinese_non_emergency_queries_retrieve_supported_sources() -> None:
    visa_snippets = search_snippets("我想查询签证和移民咨询", limit=2)
    health_snippets = search_snippets("外国人医疗保险在哪里确认", limit=2)

    assert visa_snippets
    assert health_snippets
    assert any("immigration" in snippet.topic for snippet in visa_snippets)
    assert any(snippet.topic == "health_insurance" for snippet in health_snippets)
