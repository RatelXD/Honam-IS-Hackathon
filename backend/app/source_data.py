"""Curated official-source seed snippets for deterministic retrieval.

The data in this module is intentionally static. Product code must not fetch
these URLs at request time, infer personal eligibility, or treat short seed
summaries as legal, immigration, medical, or emergency judgments.
"""

from __future__ import annotations
import hashlib

from dataclasses import dataclass
from typing import Final, Literal

SupportedLanguageCode = Literal["ko", "easy_ko", "en", "vi", "zh"]


@dataclass(frozen=True, slots=True)
class SourceSnippet:
    """A citation-ready seed excerpt from an official public institution page."""

    id: str
    source_name: str
    title: str
    source_url: str
    institution: str
    topic: str
    checked_at: str
    page_or_section: str
    quote_text: str
    keywords: tuple[str, ...]
    supported_languages: tuple[SupportedLanguageCode, ...]
    source_hash: str | None = None
    snapshot_id: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "source_hash",
            _seed_source_hash(
                self.source_url,
                self.checked_at,
                self.page_or_section,
                self.quote_text,
            ),
        )


def _seed_source_hash(source_url: str, checked_at: str, page_or_section: str, quote_text: str) -> str:
    payload = "\n".join((source_url, checked_at, page_or_section, quote_text)).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"

OFFICIAL_SOURCE_URLS: frozenset[str] = frozenset(
    {
        "https://www.hikorea.go.kr/Main.pt",
        "https://www.immigration.go.kr/immigration_eng/1862/subview.do",
        "https://www.girc.or.kr/",
        "https://www.gwangju.go.kr/eng/",
        "https://www.nhis.or.kr/english/wbheaa02900m01.do",
        "https://www.police.go.kr/eng/main.do",
        "https://www.nfa.go.kr/nfa/safetyinfo/emergencyservice/119emergencydeclaration/",
    }
)

SEED_CHECKED_AT = "2026-07-03"

SEEDED_SOURCE_SNIPPETS: tuple[SourceSnippet, ...] = (
    SourceSnippet(
        id="hikorea-portal-main",
        source_name="HiKorea",
        title="HiKorea immigration civil service portal",
        source_url="https://www.hikorea.go.kr/Main.pt",
        institution="Korea Immigration Service / Ministry of Justice",
        topic="immigration_portal",
        checked_at=SEED_CHECKED_AT,
        source_hash=None,
        snapshot_id="official-seed-20260703-hikorea-main",
        page_or_section="Main portal",
        quote_text=(
            "HiKorea is the official immigration civil service portal used as a "
            "starting point for stay, visa, and immigration-related online services."
        ),
        keywords=(
            "hikorea",
            "immigration",
            "visa",
            "stay",
            "sojourn",
            "foreign registration",
            "alien registration",
            "체류",
            "비자",
            "외국인등록",
            "출입국",
            "gia hạn visa",
            "签证",
        ),
        supported_languages=("ko", "easy_ko", "en", "vi", "zh"),
    ),
    SourceSnippet(
        id="immigration-1345-contact-center",
        source_name="Immigration Contact Center 1345",
        title="Immigration Contact Center 1345 guidance",
        source_url="https://www.immigration.go.kr/immigration_eng/1862/subview.do",
        institution="Korea Immigration Service / Ministry of Justice",
        topic="immigration_hotline",
        checked_at=SEED_CHECKED_AT,
        source_hash=None,
        snapshot_id="official-seed-20260703-immigration-1345",
        page_or_section="Immigration Contact Center",
        quote_text=(
            "The Immigration Contact Center 1345 is the official hotline for "
            "immigration and stay-related consultation; use it when personal "
            "case facts may change the answer."
        ),
        keywords=(
            "1345",
            "contact center",
            "hotline",
            "immigration consultation",
            "visa",
            "stay",
            "체류 상담",
            "출입국 상담",
            "비자 상담",
            "tư vấn nhập cư",
            "移民咨询",
        ),
        supported_languages=("ko", "easy_ko", "en", "vi", "zh"),
    ),
    SourceSnippet(
        id="girc-foreign-residents-support",
        source_name="Gwangju Foreign Residents Support Center",
        title="Gwangju Foreign Residents Support Center",
        source_url="https://www.girc.or.kr/",
        institution="Gwangju Foreign Residents Support Center",
        topic="local_support",
        checked_at=SEED_CHECKED_AT,
        source_hash=None,
        snapshot_id="official-seed-20260703-girc-home",
        page_or_section="Center homepage",
        quote_text=(
            "The Gwangju Foreign Residents Support Center is a local support "
            "institution for foreign residents seeking everyday life and "
            "administrative guidance in Gwangju."
        ),
        keywords=(
            "gwangju",
            "foreign residents",
            "support center",
            "life support",
            "administrative guidance",
            "광주",
            "외국인주민",
            "지원센터",
            "생활 상담",
            "trung tâm hỗ trợ",
            "光州",
        ),
        supported_languages=("ko", "easy_ko", "en", "vi", "zh"),
    ),
    SourceSnippet(
        id="gwangju-english-city-site",
        source_name="Gwangju Metropolitan City English Website",
        title="Gwangju Metropolitan City English site",
        source_url="https://www.gwangju.go.kr/eng/",
        institution="Gwangju Metropolitan City",
        topic="local_government",
        checked_at=SEED_CHECKED_AT,
        source_hash=None,
        snapshot_id="official-seed-20260703-gwangju-eng",
        page_or_section="English homepage",
        quote_text=(
            "Gwangju Metropolitan City's English website is an official local "
            "government channel for city information and public guidance."
        ),
        keywords=(
            "gwangju city",
            "gwangju english",
            "local government",
            "city hall",
            "public guidance",
            "광주광역시",
            "시청",
            "영어",
            "chính quyền thành phố",
            "市政府",
        ),
        supported_languages=("en", "ko", "easy_ko"),
    ),
    SourceSnippet(
        id="nhis-foreigner-guidance",
        source_name="National Health Insurance Service English",
        title="NHIS foreigner and overseas Korean guidance",
        source_url="https://www.nhis.or.kr/english/wbheaa02900m01.do",
        institution="National Health Insurance Service",
        topic="health_insurance",
        checked_at=SEED_CHECKED_AT,
        source_hash=None,
        snapshot_id="official-seed-20260703-nhis-foreigner",
        page_or_section="Foreigner guidance page",
        quote_text=(
            "NHIS provides official English guidance for foreigners and overseas "
            "Koreans about national health insurance; individual enrollment or "
            "payment questions should be checked with NHIS."
        ),
        keywords=(
            "nhis",
            "health insurance",
            "national health insurance",
            "foreigner insurance",
            "medical insurance",
            "건강보험",
            "국민건강보험",
            "외국인 건강보험",
            "bảo hiểm y tế",
            "健康保险",
            "医疗保险",
        ),
        supported_languages=("en", "ko", "easy_ko", "vi", "zh"),
    ),
    SourceSnippet(
        id="police-emergency-112",
        source_name="Korean National Police Agency English",
        title="Korean National Police Agency official English site",
        source_url="https://www.police.go.kr/eng/main.do",
        institution="Korean National Police Agency",
        topic="police_emergency",
        checked_at=SEED_CHECKED_AT,
        source_hash=None,
        snapshot_id="official-seed-20260703-police-eng",
        page_or_section="English main site",
        quote_text=(
            "The Korean National Police Agency is the official police institution; "
            "urgent crime or safety threats should be handled through emergency "
            "police channels rather than chatbot guidance."
        ),
        keywords=(
            "police",
            "112",
            "crime",
            "violence",
            "stalking",
            "threat",
            "safety",
            "경찰",
            "범죄",
            "폭력",
            "위협",
            "cảnh sát",
            "报警",
        ),
        supported_languages=("en", "ko", "easy_ko", "vi", "zh"),
    ),
    SourceSnippet(
        id="nfa-emergency-119",
        source_name="National Fire Agency 119",
        title="119 emergency declaration guidance",
        source_url="https://www.nfa.go.kr/nfa/safetyinfo/emergencyservice/119emergencydeclaration/",
        institution="National Fire Agency",
        topic="fire_medical_emergency",
        checked_at=SEED_CHECKED_AT,
        source_hash=None,
        snapshot_id="official-seed-20260703-nfa-119",
        page_or_section="119 emergency declaration",
        quote_text=(
            "The National Fire Agency provides official 119 emergency reporting "
            "guidance; fire, rescue, and urgent medical situations should go to "
            "119 first."
        ),
        keywords=(
            "119",
            "fire",
            "ambulance",
            "medical emergency",
            "rescue",
            "emergency",
            "소방",
            "구급차",
            "응급",
            "화재",
            "cấp cứu",
            "消防",
            "急救",
        ),
        supported_languages=("ko", "easy_ko", "en", "vi", "zh"),
    ),
)

SNAPSHOT_HASH_REGISTRY: Final[dict[str, str]] = {
    "official-seed-20260703-hikorea-main": "sha256:799a42b821184a9540e34f2675574b9f73821f6f7d4dbf2ccd0fe1b5dcf055c4",
    "official-seed-20260703-immigration-1345": "sha256:9644aeedc33961d469a1a8f64edaa8984ad6604c3813ff8f7cb31b9b7ee9cf30",
    "official-seed-20260703-girc-home": "sha256:ec6fdbe4eb106145dd912ac3aa8985294b204e89f5f6829e7df3a4616d729bfb",
    "official-seed-20260703-gwangju-eng": "sha256:a631672aa6c679c56600d45ce078be3958f4521627ff6b905fdd3c3cfe202a46",
    "official-seed-20260703-nhis-foreigner": "sha256:0804971861e02da1e4c9c901403ebfd16505993b5573ed03bc5cd5d40fc30ce0",
    "official-seed-20260703-police-eng": "sha256:8e2be16047d8740e843b102addf40f9fb11dbebaa6d011b40004ab7f920cc2f8",
    "official-seed-20260703-nfa-119": "sha256:27bf6338164e6197e40ebccf27608a3495a1bc6e4a45f611aac5761d76006ce9",
}
