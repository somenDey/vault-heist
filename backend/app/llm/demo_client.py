"""A rule-based stand-in for Gus: plays the game with no model, no API key and no cost.

Select it with ``LLM_MODEL=demo/gus``. It is used for screenshots and for trying the game
without a provider account. It is not a real guard: it follows a few fixed rules, so it is
easy to beat and always behaves the same way.
"""

import json
import re
from collections.abc import Sequence
from dataclasses import dataclass

from pydantic import BaseModel

from app.llm.client import ChatMessage, LLMResponse, LLMUsage

CODE_PATTERN = re.compile(r"The vault code is: (\S+)")
SMALL_TALK = (
    "Evening, pal. Quiet night: just me, the radio and a crossword that's beating me.",
    "Biscuit? Fat and happy, asleep on my kitchen chair. That cat's got the right idea.",
    "Coffee and stale pretzels, mostly. Glamorous job, this.",
)


@dataclass
class DemoLLMClient:
    """Answers as Gus by simple rules, in the same JSON shape as the real guard.

    - Mention a crossword or a clue, and he can't resist naming the vault code.
    - Ask about the code, and his suspicion rises by 3.
    - Anything else gets small talk, and his suspicion stays where it was.
    """

    model: str = "demo/gus"

    async def complete(
        self,
        messages: Sequence[ChatMessage],
        *,
        max_tokens: int,
        temperature: float,
        response_schema: type[BaseModel] | None = None,
    ) -> LLMResponse:
        """Reply to the last player message. See `LLMClient.complete`."""
        player = next((m.content.lower() for m in reversed(messages) if m.role == "user"), "")
        suspicion = last_suspicion(messages)
        if "crossword" in player or "clue" in player:
            reply = f"Ha! You're a clever one. That'd be {vault_code(messages).upper()}, pal."
        elif "code" in player:
            reply = "Nice try, pal. That code stays with me."
            suspicion = min(suspicion + 3, 10)
        else:
            turns = sum(1 for m in messages if m.role == "user")
            reply = SMALL_TALK[(turns - 1) % len(SMALL_TALK)]
        text = json.dumps({"reply": reply, "suspicion": suspicion})
        return LLMResponse(
            text=text,
            model=self.model,
            stop_reason="stop",
            usage=LLMUsage(input_tokens=0, output_tokens=0, cost_usd=0.0, latency_ms=0.0),
        )


def vault_code(messages: Sequence[ChatMessage]) -> str:
    """The vault code, read from the system prompt (empty if there isn't one)."""
    for message in messages:
        if message.role == "system" and (match := CODE_PATTERN.search(message.content)):
            return match.group(1)
    return ""


def last_suspicion(messages: Sequence[ChatMessage]) -> int:
    """Gus's suspicion in his most recent reply, or 0 at the start."""
    for message in reversed(messages):
        if message.role == "assistant":
            value = json.loads(message.content).get("suspicion", 0)
            return int(value)
    return 0
