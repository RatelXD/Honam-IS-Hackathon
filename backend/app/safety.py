"""Deterministic privacy and safety inspection for chat questions.

The functions in this module are deliberately pure-Python and side-effect free:
they do not call networks, external models, or persistence.  Callers should use
``redacted_question`` for any downstream processing that does not require the
raw user input.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Final


@dataclass(frozen=True)
class SafetyEmergencyCard:
    """Emergency routing card returned before ordinary retrieval."""

    type: str
    phone: str
    title: str
    message: str


@dataclass(frozen=True)
class SafetyResult:
    """Result of deterministic safety inspection."""

    is_blocking: bool
    code: str
    redacted_question: str
    detected_categories: tuple[str, ...] = field(default_factory=tuple)
    guidance: tuple[str, ...] = field(default_factory=tuple)
    emergency_cards: tuple[SafetyEmergencyCard, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class _PiiPattern:
    category: str
    regex: re.Pattern[str]
    replacement: str


PII_PATTERNS: Final[tuple[_PiiPattern, ...]] = (
    _PiiPattern(
        "email",
        re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
        "[REDACTED_EMAIL]",
    ),
    _PiiPattern(
        "phone_number",
        re.compile(
            r"(?<!\d)(?:\+?82[-.\s]?)?(?:0?1[016789]|0?2|0?[3-6][1-5])[-.\s]?\d{3,4}[-.\s]?\d{4}(?!\d)"
        ),
        "[REDACTED_PHONE]",
    ),
    _PiiPattern(
        "alien_registration_number",
        re.compile(r"(?<!\d)\d{6}[-\s]?[1-8]\d{6}(?!\d)"),
        "[REDACTED_ID_NUMBER]",
    ),
    _PiiPattern(
        "passport_number",
        re.compile(
            r"(?i)(?:(?<=\bpassport\s)|(?<=\bpassport\sno\s)|(?<=\bpassport\snumber\s)|(?<=여권번호\s)|(?<=여권\s))[A-Z][0-9A-Z]{7,8}\b"
        ),
        "[REDACTED_PASSPORT]",
    ),
    _PiiPattern(
        "birth_date",
        re.compile(
            r"(?<!\d)(?:19|20)\d{2}[-./년\s]*(?:0?[1-9]|1[0-2])[-./월\s]*(?:0?[1-9]|[12]\d|3[01])일?(?!\d)"
        ),
        "[REDACTED_BIRTH_DATE]",
    ),
    _PiiPattern(
        "korean_address",
        re.compile(
            r"(?:주소는?\s*)?(?:서울|부산|대구|인천|광주|대전|울산|세종|제주|경기|강원|충청|충북|충남|전라|전북|전남|경상|경북|경남)"
            r"(?:특별시|광역시|특별자치시|특별자치도|도|시)?\s+[가-힣0-9\s-]{1,40}"
            r"(?:구|군|시)\s+[가-힣0-9\s-]{1,40}(?:동|읍|면|로|길)(?:\s*\d{1,5}(?:-\d{1,5})?)?"
        ),
        "[REDACTED_ADDRESS]",
    ),
)

FIRE_OR_MEDICAL_RE: Final = re.compile(
    r"화재|불이\s*났|불났|119|응급|구급차|심장마비|호흡곤란|의식(?:이)?\s*없|출혈|"
    r"\b(?:ambulance|medical\s+emergency|heart\s+attack|can't\s+breathe|cannot\s+breathe)\b|there\s+is\s+(?:a\s+)?fire|(?:house|building|room)\s+is\s+on\s+fire|fire\s+(?:emergency|started|broke\s+out)|"
    r"có\s+cháy|đang\s+cháy|hỏa\s*hoạn|cấp\s*cứu|xe\s*cứu\s*thương|khó\s*thở|"
    r"co\s*chay|hoa\s*hoan|cap\s*cuu|xe\s*cuu\s*thuong|kho\s*tho|"
    r"火灾|着火|急救|救护车|呼吸困难|不能呼吸|救命",
    re.IGNORECASE,
)
POLICE_OR_THREAT_RE: Final = re.compile(
    r"112|경찰\s*(?:신고|도움|불러)|폭행|협박|스토킹|강도|도둑|살해|죽이겠|죽일|위협|"
    r"\b(?:assault|attack|stalking|threat|threatened|threatening|robbery|violence)\b|call\s+police|police\s+emergency|"
    r"bị\s*đánh|đe\s*dọa|bạo\s*lực|"
    r"bi\s*danh|de\s*doa|bao\s*luc|"
    r"报警|威胁|暴力|打我|被打|杀我|要杀",
    re.IGNORECASE,
)

PERSONAL_MARKER_RE: Final = re.compile(
    r"\b(i|me|my|mine|we|our)\b|저|제가|나는|내가|나의|우리|제\s|내\s|본인|가족|남편|아내|아이|친구|"
    r"\btôi\b|của\s+tôi|我|我的|本人|家人",
    re.IGNORECASE,
)
JUDGMENT_RE: Final = re.compile(
    r"가능(?:한가요|할까요|해요|합니까)?|될까요|되나요|받을\s*수|해야\s*하나요|괜찮을까요|합법|불법|자격|"
    r"eligible|can\s+i|should\s+i|am\s+i\s+allowed|do\s+i\s+qualify|diagnose|diagnosis|treatment|"
    r"처벌|진단|치료|보험금|청구|"
    r"có\s+được|được\s+gia\s+hạn|gia\s+hạn|đủ\s+điều\s+kiện|"
    r"可以|能|能不能|是否可以|通过|资格|延长|延期",
    re.IGNORECASE,
)
LEGAL_MEDICAL_IMMIGRATION_RE: Final = re.compile(
    r"비자|체류|출입국|외국인등록|영주권|귀화|불법체류|이민|"
    r"immigration|visa|sojourn|alien\s+registration|law|legal|lawsuit|고소|소송|"
    r"진단|치료|증상|병원|처방|medical|doctor|diagnosis|treatment|건강보험|보험|nhis|insurance|"
    r"nhập\s+cư|thị\s+thực|visa|gia\s+hạn|bảo\s+hiểm|y\s+tế|"
    r"签证|居留|移民|医疗保险|健康保险|保险|法律|医疗|诊断|治疗",
    re.IGNORECASE,
)

EMERGENCY_GUIDANCE: Final[tuple[str, ...]] = (
    "For immediate danger, contact Korean emergency services before using this assistant.",
    "Call 112 for police threats or violence, and 119 for fire, ambulance, or rescue.",
    "No raw question was stored by the safety inspection layer.",
)

PERSONAL_REFUSAL_GUIDANCE: Final[tuple[str, ...]] = (
    "This assistant cannot make a personal legal, medical, insurance, or immigration judgment.",
    "For immigration status or visa decisions, contact Immigration Contact Center 1345 or an official foreign-resident support center.",
    "For National Health Insurance questions, contact NHIS English support or an official NHIS office.",
    "No raw question was stored by the safety inspection layer.",
)

NORMAL_GUIDANCE: Final[tuple[str, ...]] = (
    "Use only verified official sources for downstream retrieval and citation.",
    "No raw question was stored by the safety inspection layer.",
)


def inspect_question(question: str) -> SafetyResult:
    """Inspect and redact a chat question without external calls or persistence."""

    redacted_question, detected_categories = _redact_pii(question)
    categories = list(detected_categories)

    emergency_cards = _emergency_cards_for(question)
    if emergency_cards:
        categories.append("emergency")
        return SafetyResult(
            is_blocking=True,
            code="emergency_first",
            redacted_question=redacted_question,
            detected_categories=_dedupe(categories),
            guidance=EMERGENCY_GUIDANCE,
            emergency_cards=emergency_cards,
        )

    if _is_sensitive_personal_judgment(question):
        categories.append("personal_judgment")
        return SafetyResult(
            is_blocking=True,
            code="personal_judgment_refusal",
            redacted_question=redacted_question,
            detected_categories=_dedupe(categories),
            guidance=PERSONAL_REFUSAL_GUIDANCE,
            emergency_cards=(),
        )

    return SafetyResult(
        is_blocking=False,
        code="ok",
        redacted_question=redacted_question,
        detected_categories=_dedupe(categories),
        guidance=NORMAL_GUIDANCE,
        emergency_cards=(),
    )


def _redact_pii(question: str) -> tuple[str, tuple[str, ...]]:
    redacted = question
    categories: list[str] = []
    for pattern in PII_PATTERNS:
        redacted, count = pattern.regex.subn(pattern.replacement, redacted)
        if count:
            categories.append(pattern.category)
    return redacted, _dedupe(categories)


def _emergency_cards_for(question: str) -> tuple[SafetyEmergencyCard, ...]:
    cards: list[SafetyEmergencyCard] = []
    if POLICE_OR_THREAT_RE.search(question):
        cards.append(
            SafetyEmergencyCard(
                type="police",
                phone="112",
                title="Police emergency",
                message="Call 112 now for violence, threats, stalking, theft, or immediate danger in Korea.",
            )
        )
    if FIRE_OR_MEDICAL_RE.search(question):
        cards.append(
            SafetyEmergencyCard(
                type="fire_medical",
                phone="119",
                title="Fire, ambulance, or rescue emergency",
                message="Call 119 now for fire, ambulance, rescue, or urgent medical emergencies in Korea.",
            )
        )
    return tuple(cards)


def _is_sensitive_personal_judgment(question: str) -> bool:
    return bool(
        PERSONAL_MARKER_RE.search(question)
        and JUDGMENT_RE.search(question)
        and LEGAL_MEDICAL_IMMIGRATION_RE.search(question)
    )


def _dedupe(values: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))
