"""Tests for LiteLLMClient. No network: LiteLLM's built-in mock_response is used."""

from typing import Any

import litellm
import pytest
from pydantic import SecretStr

from app.core.config import Settings
from app.game.guard import GuardReply
from app.llm.client import ChatMessage, LLMError
from app.llm.litellm_client import LiteLLMClient

pytestmark = pytest.mark.anyio

MESSAGES = [ChatMessage("system", "You are Gus."), ChatMessage("user", "Hi")]


@pytest.fixture
def captured(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """Intercept litellm.acompletion: record its arguments and return a mocked reply."""
    calls: dict[str, Any] = {}
    real_acompletion = litellm.acompletion

    async def fake_acompletion(**kwargs: Any) -> Any:
        calls.update(kwargs)
        return await real_acompletion(**kwargs, mock_response='{"reply": "No.", "suspicion": 2}')

    monkeypatch.setattr(litellm, "acompletion", fake_acompletion)
    return calls


async def test_response_is_converted_to_our_types(captured: dict[str, Any]) -> None:
    client = LiteLLMClient("anthropic/claude-haiku-4-5-20251001", api_key=SecretStr("sk-test"))

    response = await client.complete(
        MESSAGES, max_tokens=50, temperature=0.2, response_schema=GuardReply
    )

    assert response.text == '{"reply": "No.", "suspicion": 2}'
    assert response.model == "anthropic/claude-haiku-4-5-20251001"
    assert response.stop_reason == "stop"
    assert response.usage.input_tokens > 0
    assert response.usage.output_tokens > 0
    assert response.usage.latency_ms >= 0
    assert captured["api_key"] == "sk-test"
    assert captured["response_format"] is GuardReply
    assert captured["messages"][1] == {"role": "user", "content": "Hi"}


async def test_provider_errors_become_llm_error(monkeypatch: pytest.MonkeyPatch) -> None:
    async def failing_acompletion(**kwargs: Any) -> Any:
        raise RuntimeError("connection refused")

    monkeypatch.setattr(litellm, "acompletion", failing_acompletion)
    client = LiteLLMClient("anthropic/claude-haiku-4-5-20251001")

    with pytest.raises(LLMError, match="connection refused"):
        await client.complete(MESSAGES, max_tokens=50, temperature=0)


async def test_from_settings_picks_the_providers_key(captured: dict[str, Any]) -> None:
    settings = Settings(
        _env_file=None,
        llm_model="anthropic/claude-haiku-4-5-20251001",
        anthropic_api_key=SecretStr("sk-anthropic"),
        openai_api_key=SecretStr("sk-openai"),
    )

    await LiteLLMClient.from_settings(settings).complete(MESSAGES, max_tokens=50, temperature=0)

    assert captured["api_key"] == "sk-anthropic"
    assert captured["api_base"] is None


async def test_from_settings_points_ollama_at_the_local_server(captured: dict[str, Any]) -> None:
    settings = Settings(_env_file=None, llm_model="ollama_chat/granite4.2:8b")

    await LiteLLMClient.from_settings(settings).complete(MESSAGES, max_tokens=50, temperature=0)

    assert captured["api_base"] == "http://localhost:11434"
    assert captured["api_key"] is None
