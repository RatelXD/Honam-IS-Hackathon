from fastapi.testclient import TestClient

from app.main import app
from app.settings import get_settings


client = TestClient(app)


def test_health_reports_local_seeded_mode_and_zero_raw_retention() -> None:
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



def test_settings_remain_scaffold_only_even_when_env_is_present(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("RAG_INDEX_PATH", "data/index.json")

    settings = get_settings()

    assert settings.llm_provider == "openai"
    assert settings.rag_index_path == "data/index.json"
    assert settings.scaffold_only is True


def test_chat_returns_seeded_source_grounded_response() -> None:
    response = client.post(
        "/api/chat",
        json={"question": "비자 연장은 어디서 확인하나요?", "language": "ko"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["language"] == "ko"
    assert payload["citations"]
    assert payload["emergency_cards"] == []
    assert payload["safety"]["is_refusal"] is False
    assert payload["safety"]["scaffold_only"] is False
    assert payload["safety"]["raw_question_stored"] is False
    assert payload["safety"]["raw_retention_days"] == 0
    assert payload["safety"]["code"] == "ok"
    assert payload["institution_cards"][0]["reason"]
    assert "1345" in payload["answer"]
