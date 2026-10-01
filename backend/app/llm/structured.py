"""Get a validated Pydantic object out of a model: validate, retry once, then fall back."""

from collections.abc import Sequence
from dataclasses import dataclass

import structlog
from pydantic import BaseModel, ValidationError

from app.llm.client import ChatMessage, LLMClient, LLMResponse

logger = structlog.get_logger()


@dataclass(frozen=True)
class StructuredResult[T: BaseModel]:
    """The outcome of `complete_structured`.

    Attributes:
        value: The validated object, or the fallback.
        responses: Every model call made (one, or two after a retry), so their
            tokens and cost can be recorded.
        used_fallback: True if no valid reply was produced.
    """

    value: T
    responses: tuple[LLMResponse, ...]
    used_fallback: bool


async def complete_structured[T: BaseModel](
    client: LLMClient,
    messages: Sequence[ChatMessage],
    schema: type[T],
    *,
    fallback: T,
    max_tokens: int,
    temperature: float,
    max_attempts: int = 2,
) -> StructuredResult[T]:
    """Ask the model for JSON matching ``schema``, and validate what comes back.

    If a reply is invalid, the model is shown its own reply and the validation
    error and asked to try again. After ``max_attempts`` invalid replies,
    ``fallback`` is returned instead, so the caller always gets a usable value.

    Raises:
        LLMError: If a model call itself fails (network, auth, ...). Fallback
            covers bad *output*, not a failed call.
    """
    conversation = list(messages)
    responses: list[LLMResponse] = []
    for attempt in range(1, max_attempts + 1):
        response = await client.complete(
            conversation, max_tokens=max_tokens, temperature=temperature, response_schema=schema
        )
        responses.append(response)
        try:
            value = schema.model_validate_json(extract_json_object(response.text))
        except (ValueError, ValidationError) as exc:
            logger.warning(
                "structured_output_invalid",
                attempt=attempt,
                model=response.model,
                stop_reason=response.stop_reason,
                error=str(exc),
            )
            conversation = [
                *messages,
                ChatMessage("assistant", response.text),
                ChatMessage("user", _correction(exc, truncated=response.truncated)),
            ]
            continue
        return StructuredResult(value, tuple(responses), used_fallback=False)

    logger.error("structured_output_fallback", attempts=max_attempts)
    return StructuredResult(fallback, tuple(responses), used_fallback=True)


def extract_json_object(text: str) -> str:
    """Return the outermost ``{...}`` in ``text``.

    Models sometimes wrap JSON in prose or Markdown fences, e.g.
    ``Sure! ```json {...} ``` ``. This keeps just the object.

    Raises:
        ValueError: If there is no JSON object in the text.
    """
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end < start:
        raise ValueError("no JSON object found in the reply")
    return text[start : end + 1]


def _correction(error: Exception, *, truncated: bool) -> str:
    """The message sent back to the model after an invalid reply."""
    hint = " Your reply was cut off, so keep it shorter." if truncated else ""
    return (
        "Your previous reply was not valid. "
        f"Error: {error}.{hint} "
        "Reply again with only the JSON object, in the required format, and nothing else."
    )
