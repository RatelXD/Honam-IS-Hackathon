"""FastAPI entrypoint for the Honam/Gwangju RAG feasibility backend."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import (
    ChatRequest,
    ChatResponse,
    EmergencyCard,
    InstitutionCard,
    SafetyMetadata,
    SourceCitation,
)
from app.settings import get_settings

from app.retrieval import build_institution_cards, compose_grounded_answer, search_snippets, validate_citation
from app.safety import inspect_question

settings = get_settings()
RAW_RETENTION_DAYS = 0
EXTERNAL_LLM_ENABLED = False

_MESSAGE_CATALOG: dict[str, dict[str, str]] = {
    "emergency_first": {
        "ko": "긴급 상황일 수 있습니다. 일반 행정 안내보다 112 또는 119 등 긴급 연락을 먼저 이용하세요.",
        "easy_ko": "위험할 수 있습니다. 먼저 112나 119에 연락하세요.",
        "en": "This may be an emergency. Use 112 or 119 before ordinary administrative guidance.",
        "vi": "Đây có thể là tình huống khẩn cấp. Hãy gọi 112 hoặc 119 trước khi dùng hướng dẫn hành chính thông thường.",
        "zh": "这可能是紧急情况。请先拨打 112 或 119，再使用一般行政信息。",
    },
    "personal_sensitive_refusal": {
        "ko": "개인정보가 포함된 질문에는 답변하지 않습니다. 식별 정보를 제외하고 다시 묻거나 공식 기관 상담 경로를 이용하세요.",
        "easy_ko": "개인정보가 들어간 질문에는 답하지 않습니다. 이름, 번호, 주소 등을 빼고 다시 물어보세요.",
        "en": "I cannot answer a question that includes personal information. Remove identifying details or use an official agency channel.",
        "vi": "Tôi không thể trả lời câu hỏi có thông tin cá nhân. Hãy bỏ thông tin nhận dạng hoặc liên hệ cơ quan chính thức.",
        "zh": "我不能回答包含个人信息的问题。请删除身份信息，或联系官方机构。",
    },
    "personal_judgment_refusal": {
        "ko": "개인별 법률·의료·보험·체류 판단이 필요한 내용은 답변하지 않습니다. 공식 기관 상담 경로를 이용하세요.",
        "easy_ko": "개인 자격이나 결과는 제가 판단하지 않습니다. 공식 기관에 물어보세요.",
        "en": "I cannot make a personal legal, medical, insurance, or immigration judgment. Use the official agency channel.",
        "vi": "Tôi không thể kết luận về pháp lý, y tế, bảo hiểm hoặc cư trú cho trường hợp cá nhân. Hãy liên hệ cơ quan chính thức.",
        "zh": "我不能对个人法律、医疗、保险或居留问题作最终判断。请咨询官方机构。",
    },
    "scaffold_refusal": {
        "ko": "현재 로컬 공식 출처 검색 모듈을 사용할 수 없어 답변하지 않습니다. 출입국·체류 문의는 1345 또는 관할 기관에 문의하세요.",
        "easy_ko": "지금은 공식 자료 검색을 쓸 수 없어 답하지 않습니다. 1345나 기관에 물어보세요.",
        "en": "The local official-source retrieval module is unavailable, so I cannot answer. Contact 1345 or the relevant agency.",
        "vi": "Hiện chưa dùng được mô-đun tìm kiếm nguồn chính thức cục bộ nên hệ thống không trả lời. Hãy liên hệ 1345 hoặc cơ quan liên quan.",
        "zh": "当前无法使用本地官方来源检索模块，因此不能回答。请联系 1345 或相关机构。",
    },
    "source_insufficient": {
        "ko": "검증된 공식 출처를 찾지 못해 답변하지 않습니다. 1345 또는 관련 공식 기관에 문의하세요.",
        "easy_ko": "확인된 공식 자료가 부족해서 답하지 않습니다. 1345나 관련 기관에 물어보세요.",
        "en": "I could not find a validated official source, so I will not answer. Contact 1345 or the relevant official agency.",
        "vi": "Không tìm thấy nguồn chính thức đã kiểm chứng nên hệ thống không trả lời. Hãy liên hệ 1345 hoặc cơ quan liên quan.",
        "zh": "未找到已验证的官方来源，因此不回答。请联系 1345 或相关官方机构。",
    },
    "empty_answer": {
        "ko": "검증된 공식 출처 기반 답변을 구성하지 못해 답변하지 않습니다. 공식 기관 상담 경로를 이용하세요.",
        "easy_ko": "공식 자료로 답을 만들 수 없어 답하지 않습니다. 기관에 물어보세요.",
        "en": "I could not build an answer from validated official sources. Use an official agency channel.",
        "vi": "Không thể tạo câu trả lời từ nguồn chính thức đã kiểm chứng. Hãy liên hệ cơ quan chính thức.",
        "zh": "无法根据已验证官方来源生成回答。请咨询官方机构。",
    },
}

app = FastAPI(
    title="Honam/Gwangju Official-Source RAG Backend",
    version="0.1.0",
    description="Local seeded official-source retrieval API for feasibility testing.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def _read(value: Any, key: str, default: Any = None) -> Any:
    if isinstance(value, dict):
        return value.get(key, default)
    return getattr(value, key, default)

def _localized_message(language: str, code: str) -> str:
    catalog = _MESSAGE_CATALOG.get(code) or _MESSAGE_CATALOG["source_insufficient"]
    return catalog.get(language) or catalog["en"]

def _localized_emergency_card_message(language: str, card_type: str, phone: str) -> str:
    is_police = phone == "112" or "police" in card_type
    messages = {
        "ko": f"{'경찰 긴급 상황' if is_police else '화재·구급·구조 긴급 상황'}이면 {phone}에 먼저 연락하세요.",
        "easy_ko": f"위험하면 먼저 {phone}에 전화하세요.",
        "en": f"Call {phone} first for {'police threats or violence' if is_police else 'fire, ambulance, rescue, or urgent medical help'}.",
        "vi": f"Hãy gọi {phone} trước nếu cần {'cảnh sát hoặc có bạo lực/đe dọa' if is_police else 'chữa cháy, xe cứu thương, cứu hộ hoặc cấp cứu'}.",
        "zh": f"如需{'警方协助或遇到暴力威胁' if is_police else '火灾、救护、救援或紧急医疗帮助'}，请先拨打 {phone}。",
    }
    return messages.get(language) or messages["en"]

def _localized_guidance(language: str, code: str) -> list[str]:
    guidance = {
        "ko": [
            "질문 원문은 저장하지 않았습니다.",
            "외부 LLM 호출은 수행하지 않았습니다.",
            "답변은 검증된 공식 출처 또는 공식 기관 안내로 제한됩니다.",
        ],
        "easy_ko": [
            "질문 원문은 저장하지 않습니다.",
            "외부 AI 모델을 부르지 않았습니다.",
            "확인된 공식 자료나 기관 안내 안에서만 답합니다.",
        ],
        "en": [
            "No raw question was persisted.",
            "No external LLM call was made.",
            "Responses are limited to validated official sources or official agency guidance.",
        ],
        "vi": [
            "Câu hỏi gốc không được lưu.",
            "Không gọi mô hình LLM bên ngoài.",
            "Câu trả lời chỉ dựa trên nguồn chính thức đã kiểm chứng hoặc hướng dẫn của cơ quan chính thức.",
        ],
        "zh": [
            "不会保存原始问题。",
            "没有调用外部 LLM。",
            "回答仅限于已验证官方来源或官方机构指引。",
        ],
    }
    if code == "emergency_first":
        return {
            "ko": ["긴급 상황에서는 일반 안내보다 112 또는 119를 먼저 이용하세요."],
            "easy_ko": ["위험하면 먼저 112나 119에 연락하세요."],
            "en": ["For emergencies, use 112 or 119 before ordinary guidance."],
            "vi": ["Trong tình huống khẩn cấp, hãy gọi 112 hoặc 119 trước."],
            "zh": ["紧急情况下，请先拨打 112 或 119。"],
        }.get(language, ["For emergencies, use 112 or 119 before ordinary guidance."])
    return guidance.get(language) or guidance["en"]


def _is_retrieval_ready() -> bool:
    return all(
        callable(func)
        for func in (
            search_snippets,
            validate_citation,
            compose_grounded_answer,
        )
    )


def _safety_metadata(
    *,
    is_refusal: bool,
    code: str,
    redacted_question: str,
    language: str,
    detected_categories: list[str] | tuple[str, ...] = (),
) -> SafetyMetadata:
    return SafetyMetadata(
        is_refusal=is_refusal,
        code=code,
        detected_categories=list(detected_categories),
        redacted_question=redacted_question,
        raw_question_stored=False,
        raw_retention_days=RAW_RETENTION_DAYS,
        scaffold_only=not _is_retrieval_ready(),
        external_llm_enabled=EXTERNAL_LLM_ENABLED,
        provider_disabled=not EXTERNAL_LLM_ENABLED,
        guidance=_localized_guidance(language, code),
    )


def _fallback_institution_cards(reason: str, language: str) -> list[InstitutionCard]:
    descriptions = {
        "ko": (
            "출입국·체류 관련 공식 전화 상담 경로입니다.",
            "광주 외국인 주민의 행정·생활 안내를 위한 지역 지원 경로입니다.",
            "개인별 판단 대신 공식 기관 안내가 필요합니다.",
        ),
        "easy_ko": (
            "비자와 체류를 물어볼 수 있는 공식 전화입니다.",
            "광주에서 외국인 주민이 도움을 받을 수 있는 곳입니다.",
            "개인 결과는 기관에 물어봐야 합니다.",
        ),
        "en": (
            "Official phone guidance for immigration and stay-status questions.",
            "Local support path for foreign residents who need administrative or daily-life guidance in Gwangju.",
            reason,
        ),
        "vi": (
            "Kênh tư vấn điện thoại chính thức về nhập cư và tình trạng cư trú.",
            "Kênh hỗ trợ địa phương cho cư dân nước ngoài cần hướng dẫn hành chính hoặc đời sống tại Gwangju.",
            "Cần dùng hướng dẫn của cơ quan chính thức thay vì kết luận cá nhân.",
        ),
        "zh": (
            "关于出入境和居留问题的官方电话咨询渠道。",
            "光州外籍居民获得行政和生活指引的本地支持渠道。",
            "需要官方机构指引，而不是个人化最终判断。",
        ),
    }
    immigration_description, local_description, localized_reason = descriptions.get(language, descriptions["en"])
    return [
        InstitutionCard(
            name="Immigration Contact Center 1345",
            description=immigration_description,
            phone="1345",
            url="https://www.hikorea.go.kr/",
            reason=localized_reason,
        ),
        InstitutionCard(
            name="Gwangju Foreign Residents Support Center",
            description=local_description,
            phone="1644-3828",
            url="https://www.girc.or.kr/",
            reason=localized_reason,
        ),
    ]


def _emergency_cards(cards: Any, language: str) -> list[EmergencyCard]:
    emergency_cards: list[EmergencyCard] = []
    for index, card in enumerate(cards or ()):  # safety returns dataclasses, tests may return dicts.
        card_type = str(_read(card, "type", "emergency"))
        phone = str(_read(card, "phone", "119"))
        emergency_cards.append(
            EmergencyCard(
                type=card_type,
                phone=phone,
                priority=int(_read(card, "priority", index)),
                message=_localized_emergency_card_message(language, card_type, phone),
            )
        )
    return emergency_cards


def _citation_from_snippet(snippet: Any) -> SourceCitation:
    return SourceCitation(
        title=str(_read(snippet, "title", _read(snippet, "source_name", "Official source"))),
        url=str(_read(snippet, "source_url", _read(snippet, "url"))),
        institution=str(_read(snippet, "institution", _read(snippet, "source_name", "Official institution"))),
        retrieved_at=_read(snippet, "checked_at", _read(snippet, "retrieved_at")),
        excerpt=_read(snippet, "quote_text", _read(snippet, "excerpt")),
        source_hash=_read(snippet, "source_hash"),
        snapshot_id=_read(snippet, "snapshot_id"),
        page_or_section=_read(snippet, "page_or_section"),
    )


def _source_card_text(language: str, source_name: str, topic: str, quote_text: str) -> tuple[str, str]:
    topic_label = topic.replace("_", " ")
    catalog = {
        "ko": (
            f"{source_name} 공식 출처에서 확인한 {topic_label} 안내입니다.",
            "검증된 공식 출처가 이 질문과 연결되어 표시됩니다.",
        ),
        "easy_ko": (
            f"{source_name} 공식 자료에서 확인한 안내입니다.",
            "이 질문과 관련 있는 공식 자료입니다.",
        ),
        "en": (
            quote_text,
            f"Official source for {topic_label} guidance.",
        ),
        "vi": (
            f"Hướng dẫn {topic_label} đã được kiểm tra từ nguồn chính thức {source_name}.",
            "Nguồn chính thức đã kiểm chứng được liên kết với câu hỏi này.",
        ),
        "zh": (
            f"来自 {source_name} 的已验证官方{topic_label}指引。",
            "此问题已关联到已验证官方来源。",
        ),
    }
    return catalog.get(language, catalog["en"])


def _phone_for_snippet(snippet: Any) -> str | None:
    keywords = tuple(str(keyword) for keyword in _read(snippet, "keywords", ()))
    quote_text = str(_read(snippet, "quote_text", ""))
    if "1345" in keywords or "1345" in quote_text:
        return "1345"
    if "112" in keywords or "112" in quote_text:
        return "112"
    if "119" in keywords or "119" in quote_text:
        return "119"
    if str(_read(snippet, "source_name", "")) == "Gwangju Foreign Residents Support Center":
        return "1644-3828"
    return None


def _institution_cards_from_snippets(snippets: list[Any], language: str) -> list[InstitutionCard]:
    cards: list[InstitutionCard] = []
    seen_institutions: set[str] = set()
    for snippet in snippets:
        institution = str(_read(snippet, "institution", _read(snippet, "source_name", "Official institution")))
        if institution in seen_institutions:
            continue
        seen_institutions.add(institution)
        source_name = str(_read(snippet, "source_name", institution))
        topic = str(_read(snippet, "topic", "official guidance"))
        quote_text = str(_read(snippet, "quote_text", "Official guidance channel."))
        description, reason = _source_card_text(language, source_name, topic, quote_text)
        cards.append(
            InstitutionCard(
                name=source_name,
                description=description,
                phone=_phone_for_snippet(snippet),
                url=_read(snippet, "source_url", _read(snippet, "url")),
                address=None,
                reason=reason,
            )
        )
    return cards


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "service": "honam-rag-backend",
        "mode": "local_seeded_backend" if _is_retrieval_ready() else "safe_scaffold",
        "scaffold_only": not _is_retrieval_ready(),
        "raw_retention_days": RAW_RETENTION_DAYS,
        "external_llm_enabled": EXTERNAL_LLM_ENABLED,
        "provider_disabled": not EXTERNAL_LLM_ENABLED,
        "production_ready": False,
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Return deterministic safety-gated, source-grounded responses only."""

    safety_result = inspect_question(request.question) if callable(inspect_question) else None
    safety_code = str(_read(safety_result, "code", "scaffold_refusal"))
    redacted_question = str(_read(safety_result, "redacted_question", "[not stored]"))
    detected_categories = tuple(_read(safety_result, "detected_categories", ()))
    has_personal_sensitive_data = bool(detected_categories) and "emergency" not in detected_categories
    retrieval_question = redacted_question if safety_result is not None else request.question

    if _read(safety_result, "is_blocking", False):
        emergency_cards = _emergency_cards(_read(safety_result, "emergency_cards", ()), request.language.value)
        answer = _localized_message(request.language.value, safety_code)
        return ChatResponse(
            answer=answer,
            language=request.language,
            citations=[],
            institution_cards=_fallback_institution_cards("Safety policy requires agency guidance instead of a personalized answer.", request.language.value),
            emergency_cards=emergency_cards,
            safety=_safety_metadata(
                is_refusal=True,
                code=safety_code,
                redacted_question=redacted_question,
                language=request.language.value,
                detected_categories=detected_categories,
            ),
        )
    if has_personal_sensitive_data:
        return ChatResponse(
            answer=_localized_message(request.language.value, "personal_sensitive_refusal"),
            language=request.language,
            citations=[],
            institution_cards=_fallback_institution_cards("Personal sensitive data was detected; use an official agency channel instead.", request.language.value),
            emergency_cards=[],
            safety=_safety_metadata(
                is_refusal=True,
                code="personal_sensitive_refusal",
                redacted_question=redacted_question,
                language=request.language.value,
                detected_categories=detected_categories,
            ),
        )

    if not _is_retrieval_ready():
        return ChatResponse(
            answer=_localized_message(request.language.value, "scaffold_refusal"),
            language=request.language,
            citations=[],
            institution_cards=_fallback_institution_cards("Local seeded retrieval is not available for this request.", request.language.value),
            emergency_cards=[],
            safety=_safety_metadata(
                is_refusal=True,
                code="scaffold_refusal",
                redacted_question=redacted_question,
                language=request.language.value,
                detected_categories=detected_categories,
            ),
        )

    snippets = search_snippets(retrieval_question, limit=3) or []  # type: ignore[misc]
    valid_snippets = [snippet for snippet in snippets if validate_citation(snippet)]  # type: ignore[misc]
    if not valid_snippets:
        return ChatResponse(
            answer=_localized_message(request.language.value, "source_insufficient"),
            language=request.language,
            citations=[],
            institution_cards=_fallback_institution_cards("No validated official citation was available for this question.", request.language.value),
            emergency_cards=[],
            safety=_safety_metadata(
                is_refusal=True,
                code="source_insufficient",
                redacted_question=redacted_question,
                language=request.language.value,
                detected_categories=detected_categories,
            ),
        )

    answer = str(compose_grounded_answer(retrieval_question, request.language.value, valid_snippets)).strip()  # type: ignore[misc]
    if not answer:
        return ChatResponse(
            answer=_localized_message(request.language.value, "empty_answer"),
            language=request.language,
            citations=[],
            institution_cards=_fallback_institution_cards("A validated citation existed, but no grounded answer was produced.", request.language.value),
            emergency_cards=[],
            safety=_safety_metadata(
                is_refusal=True,
                code="source_insufficient",
                redacted_question=redacted_question,
                language=request.language.value,
                detected_categories=detected_categories,
            ),
        )

    return ChatResponse(
        answer=answer,
        language=request.language,
        citations=[_citation_from_snippet(snippet) for snippet in valid_snippets],
        institution_cards=_institution_cards_from_snippets(valid_snippets, request.language.value),
        emergency_cards=[],
        safety=_safety_metadata(
            is_refusal=False,
            code=safety_code if safety_code != "scaffold_refusal" else "ok",
            redacted_question=redacted_question,
            language=request.language.value,
            detected_categories=detected_categories,
        ),
    )
