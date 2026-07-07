from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fastapi.testclient import TestClient

import app.main as main
from app.main import app


client = TestClient(app)


@dataclass(frozen=True)
class FakeSafetyResult:
    is_blocking: bool = False
    code: str = "ok"
    redacted_question: str = "광주 외국인등록 지원"
    detected_categories: tuple[str, ...] = ()
    guidance: tuple[str, ...] = ()
    emergency_cards: tuple[Any, ...] = ()


@dataclass(frozen=True)
class FakeSnippet:
    title: str = "Immigration guidance"
    source_url: str = "https://www.hikorea.go.kr/"
    institution: str = "HiKorea"
    checked_at: str = "2026-07-03"
    quote_text: str = "Foreign residents can use official immigration guidance and 1345."
    source_hash: str = "sha256:seed"
    snapshot_id: str = "seed-hikorea"
    page_or_section: str = "Immigration Contact Center"


@dataclass(frozen=True)
class FakeEmergencyCard:
    type: str = "fire_medical"
    phone: str = "119"
    priority: int = 0
    message: str = "Call 119 first for urgent medical or fire emergencies."


def install_retrieval(monkeypatch, snippets: list[FakeSnippet] | None = None) -> None:
    seeded_snippets = snippets if snippets is not None else [FakeSnippet()]

    monkeypatch.setattr(main, "search_snippets", lambda query, limit=3: seeded_snippets)
    monkeypatch.setattr(main, "validate_citation", lambda snippet: True)
    monkeypatch.setattr(
        main,
        "compose_grounded_answer",
        lambda question, language, snippets: "Use official immigration/support guidance and contact 1345 for stay questions.",
    )
    monkeypatch.setattr(
        main,
        "build_institution_cards",
        lambda snippets: [
            {
                "name": "Immigration Contact Center 1345",
                "description": "Official immigration phone guidance.",
                "phone": "1345",
                "url": "https://www.hikorea.go.kr/",
                "reason": "Validated official-source snippet matched the query.",
            }
        ],
    )


def test_health_reports_local_seeded_backend_without_llm_or_raw_retention(monkeypatch) -> None:
    install_retrieval(monkeypatch)

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "honam-rag-backend"
    assert payload["mode"] == "local_seeded_backend"
    assert payload["scaffold_only"] is False
    assert payload["raw_retention_days"] == 0
    assert payload["external_llm_enabled"] is False
    assert payload["provider_disabled"] is True
    assert payload["production_ready"] is False


def test_normal_immigration_support_health_query_returns_validated_citations(monkeypatch) -> None:
    install_retrieval(
        monkeypatch,
        snippets=[
            FakeSnippet(
                title="NHIS foreign resident health insurance guidance",
                source_url="https://www.nhis.or.kr/english/",
                institution="National Health Insurance Service",
                quote_text="Foreign residents can check NHIS English guidance for health insurance.",
                snapshot_id="seed-nhis",
            )
        ],
    )
    monkeypatch.setattr(main, "inspect_question", lambda question: FakeSafetyResult(redacted_question=question))

    response = client.post(
        "/api/chat",
        json={"question": "Where can foreign residents in Gwangju check immigration support and health insurance?", "language": "en"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["language"] == "en"
    assert payload["safety"]["is_refusal"] is False
    assert payload["safety"]["code"] == "ok"
    assert payload["safety"]["raw_question_stored"] is False
    assert payload["safety"]["raw_retention_days"] == 0
    assert payload["safety"]["external_llm_enabled"] is False
    assert payload["citations"] == [
        {
            "title": "NHIS foreign resident health insurance guidance",
            "url": "https://www.nhis.or.kr/english/",
            "institution": "National Health Insurance Service",
            "retrieved_at": "2026-07-03",
            "excerpt": "Foreign residents can check NHIS English guidance for health insurance.",
            "source_hash": "sha256:seed",
            "snapshot_id": "seed-nhis",
            "page_or_section": "Immigration Contact Center",
        }
    ]
    assert payload["institution_cards"][0]["name"] == "National Health Insurance Service"
    assert payload["emergency_cards"] == []


def test_unsupported_query_refuses_when_no_validated_citation(monkeypatch) -> None:
    install_retrieval(monkeypatch, snippets=[])
    monkeypatch.setattr(main, "inspect_question", lambda question: FakeSafetyResult(redacted_question=question))

    response = client.post("/api/chat", json={"question": "Tell me the best apartment to rent", "language": "en"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["citations"] == []
    assert payload["safety"]["is_refusal"] is True
    assert payload["safety"]["code"] == "source_insufficient"
    assert "1345" in payload["institution_cards"][0]["name"]

def test_unsupported_query_refusal_is_localized_to_requested_language() -> None:
    response = client.post(
        "/api/chat",
        json={"question": "광주에서 가장 맛있는 식당을 추천해줘", "language": "en"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["safety"]["code"] == "source_insufficient"
    assert payload["safety"]["is_refusal"] is True
    assert payload["citations"] == []
    assert payload["answer"].startswith("I could not find a validated official source")


def test_lodging_stay_query_refuses_without_immigration_citations() -> None:
    response = client.post(
        "/api/chat",
        json={"question": "Where can I stay at a hotel near Gwangju Station?", "language": "en"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["safety"]["code"] == "source_insufficient"
    assert payload["safety"]["is_refusal"] is True
    assert payload["citations"] == []
    assert payload["answer"].startswith("I could not find a validated official source")

def test_korean_and_easy_korean_paths_have_grounded_and_refusal_coverage() -> None:
    grounded_cases = [
        ("ko", "공식 출처 씨앗 자료 기준 안내입니다."),
        ("easy_ko", "공식 기관 자료로만 짧게 안내합니다."),
    ]
    for language, expected_prefix in grounded_cases:
        response = client.post(
            "/api/chat",
            json={"question": "외국인 비자 상담은 어디서 해?", "language": language},
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["language"] == language
        assert payload["answer"].startswith(expected_prefix)
        assert payload["safety"]["is_refusal"] is False
        assert payload["safety"]["raw_question_stored"] is False
        assert payload["citations"]
        assert payload["institution_cards"]

    refusal_cases = [
        ("ko", "검증된 공식 출처를 찾지 못해 답변하지 않습니다."),
        ("easy_ko", "확인된 공식 자료가 부족해서 답하지 않습니다."),
    ]
    for language, expected_prefix in refusal_cases:
        response = client.post(
            "/api/chat",
            json={"question": "광주 맛집 추천해줘", "language": language},
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["answer"].startswith(expected_prefix)
        assert payload["safety"]["code"] == "source_insufficient"
        assert payload["safety"]["is_refusal"] is True
        assert payload["citations"] == []
        assert payload["emergency_cards"] == []

def test_benign_fireworks_query_is_source_insufficient_not_emergency() -> None:
    response = client.post(
        "/api/chat",
        json={"question": "Where can I watch fireworks in Gwangju this weekend?", "language": "en"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["safety"]["code"] == "source_insufficient"
    assert payload["emergency_cards"] == []


def test_chinese_and_vietnamese_personal_judgment_api_refuses() -> None:
    zh_response = client.post(
        "/api/chat",
        json={"question": "我可以延长签证吗？我的情况能通过吗？", "language": "zh"},
    )
    vi_response = client.post(
        "/api/chat",
        json={"question": "Tôi có được gia hạn visa không?", "language": "vi"},
    )

    assert zh_response.status_code == 200
    assert vi_response.status_code == 200
    assert zh_response.json()["safety"]["code"] == "personal_judgment_refusal"
    assert vi_response.json()["safety"]["code"] == "personal_judgment_refusal"
    assert zh_response.json()["citations"] == []
    assert vi_response.json()["citations"] == []


def test_emergency_refusal_is_localized_to_requested_language(monkeypatch) -> None:
    install_retrieval(monkeypatch)
    monkeypatch.setattr(
        main,
        "inspect_question",
        lambda question: FakeSafetyResult(
            is_blocking=True,
            code="emergency_first",
            redacted_question="Có cháy",
            detected_categories=("emergency",),
            emergency_cards=(FakeEmergencyCard(),),
        ),
    )

    response = client.post("/api/chat", json={"question": "Có cháy", "language": "vi"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["safety"]["code"] == "emergency_first"
    assert payload["answer"].startswith("Đây có thể")

def test_real_vietnamese_emergency_question_routes_without_monkeypatch() -> None:
    response = client.post("/api/chat", json={"question": "Có cháy trong nhà tôi", "language": "vi"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["safety"]["code"] == "emergency_first"
    assert payload["emergency_cards"][0]["phone"] == "119"
    assert payload["answer"].startswith("Đây có thể")


def test_personal_sensitive_question_is_refused_with_redacted_payload(monkeypatch) -> None:
    install_retrieval(monkeypatch)
    monkeypatch.setattr(
        main,
        "inspect_question",
        lambda question: FakeSafetyResult(
            is_blocking=True,
            code="personal_sensitive_refusal",
            redacted_question="My ARC number is [REDACTED]. Should I change visa?",
            detected_categories=("personal_identifier", "visa_judgment"),
            guidance=("Use an official agency channel for personal immigration judgment.",),
        ),
    )

    response = client.post(
        "/api/chat",
        json={"question": "My ARC number is 123456-7890123. Should I change visa?", "language": "en"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["citations"] == []
    assert payload["safety"]["is_refusal"] is True
    assert payload["safety"]["code"] == "personal_sensitive_refusal"
    assert payload["safety"]["detected_categories"] == ["personal_identifier", "visa_judgment"]
    assert payload["safety"]["redacted_question"] == "My ARC number is [REDACTED]. Should I change visa?"
    assert "123456-7890123" not in str(payload)


def test_emergency_question_returns_emergency_first_cards(monkeypatch) -> None:
    install_retrieval(monkeypatch)
    monkeypatch.setattr(
        main,
        "inspect_question",
        lambda question: FakeSafetyResult(
            is_blocking=True,
            code="emergency_first",
            redacted_question="Someone is hurt",
            detected_categories=("emergency",),
            emergency_cards=(FakeEmergencyCard(),),
        ),
    )

    response = client.post("/api/chat", json={"question": "Someone is hurt and there is a fire", "language": "en"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["safety"]["code"] == "emergency_first"
    assert payload["emergency_cards"] == [
        {
            "type": "fire_medical",
            "phone": "119",
            "priority": 0,
            "message": "Call 119 first for fire, ambulance, rescue, or urgent medical help.",
        }
    ]
    assert payload["citations"] == []


def test_invalid_language_is_rejected() -> None:
    response = client.post("/api/chat", json={"question": "비자 문의", "language": "ja"})

    assert response.status_code == 422


def test_raw_question_is_not_stored_or_echoed_for_refusal(monkeypatch) -> None:
    install_retrieval(monkeypatch, snippets=[])
    monkeypatch.setattr(
        main,
        "inspect_question",
        lambda question: FakeSafetyResult(
            redacted_question="My phone is [REDACTED]",
            detected_categories=("personal_contact",),
        ),
    )

    response = client.post("/api/chat", json={"question": "My phone is 010-1234-5678", "language": "en"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["safety"]["raw_question_stored"] is False
    assert payload["safety"]["raw_retention_days"] == 0
    assert payload["safety"]["redacted_question"] == "My phone is [REDACTED]"
    assert "010-1234-5678" not in str(payload)
