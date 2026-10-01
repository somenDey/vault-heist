"""A scripted `LLMClient` for tests: no network, no cost, fully predictable."""

from collections.abc import Sequence
from dataclasses import dataclass, field

from pydantic import BaseModel

from app.llm.client import ChatMessage, LLMError, LLMResponse, LLMUsage


@dataclass(frozen=True)
class RecordedCall:
    """The arguments of one call made to a `FakeLLMClient`."""

    messages: tuple[ChatMessage, ...]
    max_tokens: int
    temperature: float
    response_schema: type[BaseModel] | None


@dataclass
class FakeLLMClient:
    """Returns pre-written replies, in order, and records every call.

    Example:
        >>> client = FakeLLMClient(replies=['{"reply": "No.", "suspicion": 2}'])
    """

    replies: list[str]
    model: str = "fake/model"
    stop_reason: str = "stop"
    calls: list[RecordedCall] = field(default_factory=list)

    async def complete(
        self,
        messages: Sequence[ChatMessage],
        *,
        max_tokens: int,
        temperature: float,
        response_schema: type[BaseModel] | None = None,
    ) -> LLMResponse:
        """Return the next scripted reply. See `LLMClient.complete`."""
        self.calls.append(RecordedCall(tuple(messages), max_tokens, temperature, response_schema))
        if not self.replies:
            raise LLMError("FakeLLMClient has no scripted replies left")
        text = self.replies.pop(0)
        return LLMResponse(
            text=text,
            model=self.model,
            stop_reason=self.stop_reason,
            usage=LLMUsage(
                input_tokens=sum(len(m.content.split()) for m in messages),
                output_tokens=len(text.split()),
                cost_usd=0.0,
                latency_ms=0.0,
            ),
        )
