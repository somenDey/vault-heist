import pytest

from app.llm.client import ChatMessage, LLMError
from app.llm.fake_client import FakeLLMClient

pytestmark = pytest.mark.anyio


async def test_returns_scripted_replies_in_order_and_records_calls() -> None:
    client = FakeLLMClient(replies=["first", "second"])
    messages = [ChatMessage("user", "hello there")]

    one = await client.complete(messages, max_tokens=10, temperature=0)
    two = await client.complete(messages, max_tokens=10, temperature=0)

    assert (one.text, two.text) == ("first", "second")
    assert len(client.calls) == 2
    assert client.calls[0].messages == tuple(messages)


async def test_raises_when_out_of_replies() -> None:
    client = FakeLLMClient(replies=[])

    with pytest.raises(LLMError):
        await client.complete([ChatMessage("user", "hi")], max_tokens=10, temperature=0)
