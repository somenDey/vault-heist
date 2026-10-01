import pytest

from app.game.guard import GuardReply, fallback_reply
from app.llm.client import ChatMessage
from app.llm.fake_client import FakeLLMClient
from app.llm.structured import StructuredResult, complete_structured, extract_json_object

pytestmark = pytest.mark.anyio

MESSAGES = [ChatMessage("system", "You are Gus."), ChatMessage("user", "Hi")]
VALID = '{"reply": "Evening, pal.", "suspicion": 1}'


async def ask(client: FakeLLMClient) -> StructuredResult[GuardReply]:
    return await complete_structured(
        client, MESSAGES, GuardReply, fallback=fallback_reply(3), max_tokens=100, temperature=0.5
    )


async def test_valid_reply_is_returned_after_one_call() -> None:
    client = FakeLLMClient(replies=[VALID])

    result = await ask(client)

    assert result.value == GuardReply(reply="Evening, pal.", suspicion=1)
    assert not result.used_fallback
    assert len(result.responses) == 1
    assert client.calls[0].response_schema is GuardReply


async def test_invalid_reply_is_retried_with_the_error_shown_to_the_model() -> None:
    client = FakeLLMClient(replies=["Sorry, no JSON here", VALID])

    result = await ask(client)

    assert result.value.reply == "Evening, pal."
    assert len(result.responses) == 2
    retry_messages = client.calls[1].messages
    assert retry_messages[-2] == ChatMessage("assistant", "Sorry, no JSON here")
    assert retry_messages[-1].role == "user"
    assert "not valid" in retry_messages[-1].content


async def test_two_invalid_replies_fall_back_without_changing_suspicion() -> None:
    client = FakeLLMClient(replies=["nope", '{"reply": "Hi", "suspicion": 99}'])

    result = await ask(client)

    assert result.used_fallback
    assert result.value == fallback_reply(3)
    assert len(result.responses) == 2


async def test_truncated_reply_asks_the_model_to_be_shorter() -> None:
    client = FakeLLMClient(
        replies=['{"reply": "Well, pal, let me tell you abo'], stop_reason="length"
    )
    client.replies.append(VALID)

    await ask(client)

    assert "shorter" in client.calls[1].messages[-1].content


def test_json_is_extracted_from_markdown_fences() -> None:
    text = 'Sure!\n```json\n{"reply": "No.", "suspicion": 2}\n```'

    assert extract_json_object(text) == '{"reply": "No.", "suspicion": 2}'


def test_text_without_json_is_rejected() -> None:
    with pytest.raises(ValueError, match="no JSON object"):
        extract_json_object("No braces at all")
