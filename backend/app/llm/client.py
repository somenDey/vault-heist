"""Our provider-agnostic interface to language models.

Everything outside ``app/llm`` depends on these types, never on a provider SDK.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal, Protocol

from pydantic import BaseModel

Role = Literal["system", "user", "assistant"]


@dataclass(frozen=True)
class ChatMessage:
    """One message in a conversation."""

    role: Role
    content: str


@dataclass(frozen=True)
class LLMUsage:
    """What one model call cost us.

    Attributes:
        input_tokens: Tokens sent to the model (system prompt + history + new message).
        output_tokens: Tokens the model generated.
        cost_usd: Price of the call in US dollars; ``None`` if the provider's price is unknown.
        latency_ms: Wall-clock time from request to complete response.
    """

    input_tokens: int
    output_tokens: int
    cost_usd: float | None
    latency_ms: float


@dataclass(frozen=True)
class LLMResponse:
    """The result of one model call.

    Attributes:
        text: The generated text.
        model: The model that produced it.
        stop_reason: Why generation stopped, e.g. ``"stop"`` (finished) or
            ``"length"`` (hit ``max_tokens``, so the text is cut off).
        usage: Tokens, cost and latency.
    """

    text: str
    model: str
    stop_reason: str | None
    usage: LLMUsage

    @property
    def truncated(self) -> bool:
        """Whether the reply was cut off by the ``max_tokens`` limit."""
        return self.stop_reason == "length"


class LLMError(Exception):
    """A model call failed: network error, bad API key, rate limit, timeout, etc."""


class LLMClient(Protocol):
    """Anything that can complete a conversation."""

    async def complete(
        self,
        messages: Sequence[ChatMessage],
        *,
        max_tokens: int,
        temperature: float,
        response_schema: type[BaseModel] | None = None,
    ) -> LLMResponse:
        """Generate the next assistant message.

        Args:
            messages: The conversation so far, starting with the system prompt.
            max_tokens: Hard limit on the length (and so the cost) of the reply.
            temperature: Randomness, from 0 (most predictable) upwards.
            response_schema: If given, ask the model to reply with JSON matching
                this Pydantic model. Not every provider can enforce it, so callers
                must still validate the reply.

        Raises:
            LLMError: If the call fails.
        """
        ...
