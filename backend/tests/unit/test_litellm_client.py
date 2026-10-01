"""Tests for LiteLLMClient. No network: litellm.acompletion is replaced with a stub."""

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
    """Replace litellm.acompletion: record its arguments and return a canned response.

    The response is a real LiteLLM ``ModelResponse``, so the conversion to our types
    is tested, but nothing is sent anywhere (not even to a local Ollama server).
    """
    calls: dict[str, Any] = {}

    async def fake_acompletion(**kwargs: Any) -> litellm.ModelResponse:
        calls.update(kwargs)
        return litellm.ModelResponse(
            model=kwargs["model"],
            choices=[
                {
                    "message": {"role": "assistant", "content": '{"reply": "No.", "suspicion": 2}'},
                    "finish_reason": "stop",
                }
            ],
            usage={"prompt_tokens": 410, "completion_tokens": 22, "total_tokens": 432},
        )

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
    assert (response.usage.input_tokens, response.usage.output_tokens) == (410, 22)
    assert response.usage.cost_usd is not None  # Haiku is in LiteLLM's price list
    assert response.usage.cost_usd > 0
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


async def test_local_models_cost_nothing_and_skip_the_price_lookup(
    captured: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    def price_lookup(**kwargs: Any) -> float:
        raise AssertionError("LiteLLM's price lookup should not be called for local models")

    monkeypatch.setattr(litellm, "completion_cost", price_lookup)
    client = LiteLLMClient("ollama_chat/granite4.2:8b")

    response = await client.complete(MESSAGES, max_tokens=50, temperature=0)

    assert response.usage.cost_usd == 0.0
