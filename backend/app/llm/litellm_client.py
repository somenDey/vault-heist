"""`LLMClient` implementation backed by LiteLLM, which speaks to every provider."""

import os
import time
from collections.abc import Sequence
from typing import Any

from pydantic import BaseModel, SecretStr

from app.core.config import Settings
from app.llm.client import ChatMessage, LLMError, LLMResponse, LLMUsage

# Use the price list bundled with LiteLLM instead of downloading it on import.
# Must be set before litellm is imported.
os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")

import litellm

litellm.suppress_debug_info = True


class LiteLLMClient:
    """Calls any model LiteLLM supports.

    Model names have a provider prefix, e.g. ``anthropic/claude-haiku-4-5-20251001``
    or ``ollama_chat/granite4.2:8b``.
    """

    def __init__(
        self,
        model: str,
        *,
        api_key: SecretStr | None = None,
        api_base: str | None = None,
        timeout_seconds: float = 30.0,
    ) -> None:
        self._model = model
        self._api_key = api_key
        self._api_base = api_base
        self._timeout_seconds = timeout_seconds

    @classmethod
    def from_settings(cls, settings: Settings) -> "LiteLLMClient":
        """Build a client for ``settings.llm_model``, with that provider's key."""
        provider = litellm.get_llm_provider(settings.llm_model)[1]
        api_keys: dict[str, SecretStr | None] = {
            "anthropic": settings.anthropic_api_key,
            "openai": settings.openai_api_key,
            "gemini": settings.gemini_api_key,
        }
        is_ollama = provider.startswith("ollama")
        return cls(
            settings.llm_model,
            api_key=api_keys.get(provider),
            api_base=settings.ollama_api_base if is_ollama else None,
            timeout_seconds=settings.llm_timeout_seconds,
        )

    async def complete(
        self,
        messages: Sequence[ChatMessage],
        *,
        max_tokens: int,
        temperature: float,
        response_schema: type[BaseModel] | None = None,
    ) -> LLMResponse:
        """Generate the next assistant message. See `LLMClient.complete`."""
        started = time.perf_counter()
        try:
            response = await litellm.acompletion(
                model=self._model,
                messages=[{"role": m.role, "content": m.content} for m in messages],
                max_tokens=max_tokens,
                temperature=temperature,
                response_format=response_schema,
                # Ask "thinking" models to answer directly: thinking costs tokens
                # and time, and some models leak it into the reply.
                reasoning_effort="none",
                # Silently skip any parameter a provider doesn't support.
                drop_params=True,
                api_key=self._api_key.get_secret_value() if self._api_key else None,
                api_base=self._api_base,
                timeout=self._timeout_seconds,
            )
        except Exception as exc:  # LiteLLM raises many types; callers see one.
            raise LLMError(f"{type(exc).__name__}: {exc}") from exc
        latency_ms = (time.perf_counter() - started) * 1000
        return self._to_llm_response(response, latency_ms)

    def _to_llm_response(self, response: Any, latency_ms: float) -> LLMResponse:
        """Convert LiteLLM's OpenAI-style response into our own type."""
        choice = response.choices[0]
        usage = getattr(response, "usage", None)
        return LLMResponse(
            text=choice.message.content or "",
            model=self._model,
            stop_reason=choice.finish_reason,
            usage=LLMUsage(
                input_tokens=getattr(usage, "prompt_tokens", 0) or 0,
                output_tokens=getattr(usage, "completion_tokens", 0) or 0,
                cost_usd=self._cost_of(response),
                latency_ms=latency_ms,
            ),
        )

    @staticmethod
    def _cost_of(response: Any) -> float | None:
        """Price the call from LiteLLM's price list; ``None`` if the model isn't listed."""
        try:
            return float(litellm.completion_cost(completion_response=response))
        except Exception:  # Unknown model or missing usage: cost is simply unknown.
            return None
