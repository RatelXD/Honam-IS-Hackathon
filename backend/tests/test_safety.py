from app.safety import inspect_question


def _combined_guidance_and_cards(result) -> str:
    card_values: list[str] = []
    for card in result.emergency_cards:
        card_values.extend([card.type, card.phone, card.title, card.message])
    return "\n".join([*result.guidance, *card_values])


def test_pii_is_redacted_and_categories_are_reported() -> None:
    raw_question = (
        "제 전화번호는 010-1234-5678, email is user@example.com, "
        "외국인등록번호 900101-5123456, 여권 M12345678, "
        "생년월일 1990년 1월 2일, 주소는 광주광역시 북구 용봉로 77 입니다."
    )

    result = inspect_question(raw_question)

    assert result.is_blocking is False
    assert result.code == "ok"
    assert result.redacted_question == (
        "제 전화번호는 [REDACTED_PHONE], email is [REDACTED_EMAIL], "
        "외국인등록번호 [REDACTED_ID_NUMBER], 여권 [REDACTED_PASSPORT], "
        "생년월일 [REDACTED_BIRTH_DATE], [REDACTED_ADDRESS] 입니다."
    )
    assert result.detected_categories == (
        "email",
        "phone_number",
        "alien_registration_number",
        "passport_number",
        "birth_date",
        "korean_address",
    )


def test_emergency_routes_to_112_and_119_before_rag() -> None:
    result = inspect_question("집에 불이 났고 누가 저를 위협해요. 바로 도움이 필요합니다.")

    assert result.is_blocking is True
    assert result.code == "emergency_first"
    assert "emergency" in result.detected_categories
    assert [card.phone for card in result.emergency_cards] == ["112", "119"]
    assert result.emergency_cards[0].type == "police"
    assert result.emergency_cards[1].type == "fire_medical"


def test_sensitive_personal_judgment_is_blocked_with_official_guidance() -> None:
    result = inspect_question("제가 D-10 비자를 연장 받을 수 있나요? 건강보험 자격도 알려주세요.")

    assert result.is_blocking is True
    assert result.code == "personal_judgment_refusal"
    assert "personal_judgment" in result.detected_categories
    assert result.emergency_cards == ()
    assert any("1345" in item for item in result.guidance)
    assert any("NHIS" in item for item in result.guidance)


def test_non_sensitive_normal_question_passes_through() -> None:
    raw_question = "광주 외국인 주민센터 운영시간은 어디에서 확인하나요?"

    result = inspect_question(raw_question)

    assert result.is_blocking is False
    assert result.code == "ok"
    assert result.redacted_question == raw_question
    assert result.detected_categories == ()
    assert result.emergency_cards == ()


def test_raw_question_is_not_present_in_guidance_or_emergency_cards() -> None:
    raw_question = "010-7777-8888 번호로 연락했고 집에 불이 났어요"

    result = inspect_question(raw_question)

    assert result.code == "emergency_first"
    combined = _combined_guidance_and_cards(result)
    assert raw_question not in combined
    assert "010-7777-8888" not in combined
    assert result.redacted_question == "[REDACTED_PHONE] 번호로 연락했고 집에 불이 났어요"

def test_vietnamese_and_chinese_emergency_terms_route_first() -> None:
    vi_result = inspect_question("Có cháy trong nhà tôi")
    zh_result = inspect_question("有人威胁我，请报警")

    assert vi_result.code == "emergency_first"
    assert vi_result.emergency_cards[0].phone == "119"
    assert zh_result.code == "emergency_first"
    assert zh_result.emergency_cards[0].phone == "112"

def test_unaccented_vietnamese_and_common_chinese_emergency_variants_route_first() -> None:
    unaccented_fire = inspect_question("Co chay trong nha toi")
    unaccented_threat = inspect_question("Toi bi de doa, canh sat giup toi")
    chinese_breathing = inspect_question("我不能呼吸，需要救命")
    chinese_assault = inspect_question("我被打了，有人要杀我")

    assert unaccented_fire.code == "emergency_first"
    assert unaccented_fire.emergency_cards[0].phone == "119"
    assert unaccented_threat.code == "emergency_first"
    assert unaccented_threat.emergency_cards[0].phone == "112"
    assert chinese_breathing.code == "emergency_first"
    assert chinese_breathing.emergency_cards[0].phone == "119"
    assert chinese_assault.code == "emergency_first"
    assert chinese_assault.emergency_cards[0].phone == "112"

def test_english_threatened_word_routes_to_112() -> None:
    result = inspect_question("I am being threatened right now. Who should I contact first?")

    assert result.code == "emergency_first"
    assert result.emergency_cards[0].phone == "112"

def test_benign_chinese_help_and_police_information_queries_do_not_route_emergency() -> None:
    generic_help = inspect_question("请帮忙告诉我外国人登记在哪里办理")
    police_information = inspect_question("请介绍光州警察博物馆的位置")

    assert generic_help.code == "ok"
    assert generic_help.emergency_cards == ()
    assert police_information.code == "ok"
    assert police_information.emergency_cards == ()

def test_benign_fireworks_and_police_museum_queries_do_not_route_emergency() -> None:
    fireworks = inspect_question("Where can I watch fireworks in Gwangju this weekend?")
    police_museum = inspect_question("Tell me about police museum souvenirs in Gwangju")

    assert fireworks.code == "ok"
    assert fireworks.emergency_cards == ()
    assert police_museum.code == "ok"
    assert police_museum.emergency_cards == ()
    fire_station = inspect_question("Tell me about the fire station museum in Gwangju")
    assert fire_station.code == "ok"
    assert fire_station.emergency_cards == ()


def test_benign_vietnamese_police_and_fire_information_queries_do_not_route_emergency() -> None:
    police_information = inspect_question("Cho tôi biết thông tin về bảo tàng cảnh sát ở Gwangju")
    fire_information = inspect_question("Tôi muốn biết thông tin về bảo tàng phòng cháy ở Gwangju")

    assert police_information.code == "ok"
    assert police_information.emergency_cards == ()
    assert fire_information.code == "ok"
    assert fire_information.emergency_cards == ()

def test_chinese_and_vietnamese_personal_judgment_requests_refuse() -> None:
    zh_result = inspect_question("我可以延长签证吗？我的情况能通过吗？")
    vi_result = inspect_question("Tôi có được gia hạn visa không?")

    assert zh_result.code == "personal_judgment_refusal"
    assert vi_result.code == "personal_judgment_refusal"
