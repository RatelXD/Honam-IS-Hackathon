"""Deterministic seeded-source retrieval helpers.

This module performs no network access and makes no LLM calls. It only ranks
curated official-source snippets from :mod:`app.source_data` and composes
source-bounded guidance that refuses personal legal, immigration, medical, or
safety judgments.
"""

from __future__ import annotations

import re
from collections import OrderedDict

from app.source_data import (
    OFFICIAL_SOURCE_URLS,
    SEEDED_SOURCE_SNIPPETS,
    SNAPSHOT_HASH_REGISTRY,
    SourceSnippet,
    _seed_source_hash,
)

SUPPORTED_LANGUAGE_CODES = {"ko", "easy_ko", "en", "vi", "zh"}
_WORD_RE = re.compile(r"[0-9A-Za-z가-힣\u4e00-\u9fff]+")
_DOMAIN_TERM_INPUTS = (
        "immigration",
        "visa",
        "stay",
        "sojourn",
        "foreign registration",
        "alien registration",
        "foreign resident",
        "support center",
        "consultation",
        "administrative guidance",
        "life support",
        "health insurance",
        "national health insurance",
        "nhis",
        "crime",
        "violence",
        "threat",
        "emergency",
        "ambulance",
        "rescue",
        "체류",
        "비자",
        "출입국",
        "외국인등록",
        "외국인 주민",
        "외국인주민",
        "지원센터",
        "상담",
        "통번역",
        "생활 민원",
        "행정서비스",
        "건강보험",
        "국민건강보험",
        "경찰",
        "범죄",
        "폭력",
        "위협",
        "응급",
        "화재",
        "구급",
        "tư vấn",
        "nhập cư",
        "bảo hiểm y tế",
        "签证",
        "移民",
        "健康保险",
        "医疗保险",
        "报警",
        "急救",
    )


def _normalize(value: str) -> str:
    return " ".join(_WORD_RE.findall(value.casefold()))

_DOMAIN_TERMS = tuple(_normalize(term) for term in _DOMAIN_TERM_INPUTS)


def _tokens(value: str) -> set[str]:
    return set(_normalize(value).split())


def _has_supported_domain(query: str) -> bool:
    query_normalized = _normalize(query)
    return any(term and term in query_normalized for term in _DOMAIN_TERMS)


def _score_snippet(query: str, snippet: SourceSnippet) -> int:
    query_normalized = _normalize(query)
    query_tokens = _tokens(query)
    if not query_normalized or not query_tokens:
        return 0

    score = 0
    searchable_fields = (
        snippet.id,
        snippet.source_name,
        snippet.title,
        snippet.institution,
        snippet.topic,
        snippet.page_or_section,
        snippet.quote_text,
    )
    searchable_text = _normalize(" ".join(searchable_fields))
    searchable_tokens = _tokens(searchable_text)

    score += 2 * len(query_tokens & searchable_tokens)

    for keyword in snippet.keywords:
        keyword_normalized = _normalize(keyword)
        if not keyword_normalized:
            continue
        keyword_tokens = _tokens(keyword_normalized)
        if keyword_normalized in query_normalized:
            score += 6
        elif query_tokens & keyword_tokens:
            score += 3

    if snippet.topic in query_normalized:
        score += 2

    return score


def search_snippets(query: str, limit: int = 3) -> list[SourceSnippet]:
    """Return deterministic official-source snippets ranked by keyword match."""

    if limit <= 0:
        return []

    if not _has_supported_domain(query):
        return []
    ranked = [
        (score, index, snippet)
        for index, snippet in enumerate(SEEDED_SOURCE_SNIPPETS)
        if (score := _score_snippet(query, snippet)) > 0
    ]
    ranked.sort(key=lambda item: (-item[0], item[1]))
    return [snippet for _, _, snippet in ranked[:limit]]


def validate_citation(snippet: SourceSnippet) -> bool:
    """Return whether a snippet has enough real metadata to be cited."""

    required_text_fields = (
        snippet.id,
        snippet.source_name,
        snippet.title,
        snippet.source_url,
        snippet.institution,
        snippet.topic,
        snippet.checked_at,
        snippet.page_or_section,
        snippet.quote_text,
    )
    expected_hash = _seed_source_hash(
        snippet.source_url,
        snippet.checked_at,
        snippet.page_or_section,
        snippet.quote_text,
    )
    return all(field.strip() for field in required_text_fields) and all(
        (
            snippet.source_url in OFFICIAL_SOURCE_URLS,
            snippet.source_hash == expected_hash,
            bool(snippet.snapshot_id),
            SNAPSHOT_HASH_REGISTRY.get(snippet.snapshot_id or "") == snippet.source_hash,
            bool(snippet.keywords),
            bool(snippet.supported_languages),
            set(snippet.supported_languages).issubset(SUPPORTED_LANGUAGE_CODES),
        )
    )


def compose_grounded_answer(
    question: str,
    language: str,
    snippets: list[SourceSnippet],
) -> str:
    """Compose a source-only answer that avoids final personal judgments."""

    valid_snippets = [snippet for snippet in snippets if validate_citation(snippet)]
    language_code = language if language in SUPPORTED_LANGUAGE_CODES else "en"

    if not valid_snippets:
        return _source_insufficient_message(language_code)

    source_lines = [
        f"- {snippet.title} ({snippet.institution}): {snippet.quote_text} [{snippet.source_url}]"
        for snippet in valid_snippets
    ]
    sources = "\n".join(source_lines)
    question_note = "" if not question.strip() else _question_scope_note(language_code)

    if language_code == "ko":
        return (
            "공식 출처 씨앗 자료 기준 안내입니다. 개인의 비자, 체류, 보험, 법률, 의료 "
            "자격에 대한 최종 판단은 하지 않습니다.\n"
            f"{question_note}"
            "확인된 출처:\n"
            f"{sources}\n"
            "개인 상황이 결과를 바꿀 수 있으면 해당 기관에 직접 문의하세요."
        )
    if language_code == "easy_ko":
        return (
            "공식 기관 자료로만 짧게 안내합니다. 당신의 자격이나 결과를 제가 결정하지 않습니다.\n"
            f"{question_note}"
            "확인한 곳:\n"
            f"{sources}\n"
            "개인 상황은 기관에 물어보세요."
        )
    if language_code == "vi":
        return (
            "Đây chỉ là hướng dẫn dựa trên nguồn chính thức đã lưu sẵn. Hệ thống "
            "không đưa ra kết luận cuối cùng về tư cách visa, cư trú, bảo hiểm, "
            "pháp lý hoặc y tế của cá nhân.\n"
            f"{question_note}"
            "Nguồn đã kiểm tra:\n"
            f"{sources}\n"
            "Nếu hoàn cảnh cá nhân có thể thay đổi kết quả, hãy liên hệ trực tiếp cơ quan liên quan."
        )
    if language_code == "zh":
        return (
            "这是基于已保存官方来源的有限说明。系统不会对个人签证、居留、保险、法律或医疗资格作最终判断。\n"
            f"{question_note}"
            "已确认来源：\n"
            f"{sources}\n"
            "如果个人情况会影响结果，请直接咨询相关官方机构。"
        )
    return (
        "This is source-only guidance from seeded official sources. It does not make "
        "a final judgment about personal visa, stay, insurance, legal, medical, or "
        "safety eligibility.\n"
        f"{question_note}"
        "Checked sources:\n"
        f"{sources}\n"
        "Contact the relevant institution directly when personal facts may change the answer."
    )


def _question_scope_note(language: str) -> str:
    if language == "ko":
        return "질문은 저장하지 않고, 아래 출처 범위 안에서만 안내합니다.\n"
    if language == "easy_ko":
        return "질문은 저장하지 않습니다. 아래 자료 안에서만 답합니다.\n"
    if language == "vi":
        return "Câu hỏi không được lưu; câu trả lời chỉ nằm trong phạm vi các nguồn dưới đây.\n"
    if language == "zh":
        return "问题不会被保存；回答只限于以下来源范围。\n"
    return "The raw question is not stored; the answer is limited to the sources below.\n"


def _source_insufficient_message(language: str) -> str:
    if language == "ko":
        return "공식 출처가 충분하지 않아 답변할 수 없습니다. 추측하지 말고 관련 기관에 문의하세요."
    if language == "easy_ko":
        return "확인된 공식 자료가 부족합니다. 추측하지 않습니다. 기관에 물어보세요."
    if language == "vi":
        return "Không đủ nguồn chính thức để trả lời. Hãy liên hệ cơ quan liên quan thay vì dựa vào phỏng đoán."
    if language == "zh":
        return "官方来源不足，无法回答。请咨询相关机构，不要依赖猜测。"
    return "There is not enough official-source evidence to answer. Please contact the relevant institution."


def build_institution_cards(snippets: list[SourceSnippet]) -> list[dict[str, object]]:
    """Build unique institution handoff cards from valid snippets."""

    cards: OrderedDict[str, dict[str, object]] = OrderedDict()
    for snippet in snippets:
        if not validate_citation(snippet):
            continue
        if snippet.institution in cards:
            continue

        card: dict[str, object] = {
            "name": snippet.source_name,
            "description": snippet.quote_text,
            "url": snippet.source_url,
            "reason": f"Official source for {snippet.topic.replace('_', ' ')} guidance.",
        }
        if "1345" in snippet.keywords or "1345" in snippet.quote_text:
            card["phone"] = "1345"
        elif snippet.source_name == "Gwangju Foreign Residents Support Center":
            card["phone"] = "1644-3828"
        elif "112" in snippet.keywords or "112" in snippet.quote_text:
            card["phone"] = "112"
        elif "119" in snippet.keywords or "119" in snippet.quote_text:
            card["phone"] = "119"

        cards[snippet.institution] = card

    return list(cards.values())
