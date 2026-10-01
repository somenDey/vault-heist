"""Chat with Gus the guard in the terminal.

Run from the repo root with ``just chat``, or from ``backend/``:

    uv run python -m scripts.chat_cli
    uv run python -m scripts.chat_cli --model ollama_chat/granite4.2:8b

Commands: /reset (start over), /quit (or Ctrl+C).
"""

import argparse
import asyncio

from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.game.guard import GuardReply, fallback_reply, load_prompt
from app.llm.client import ChatMessage, LLMError, LLMResponse
from app.llm.litellm_client import LiteLLMClient
from app.llm.structured import complete_structured

DIM, RESET = "\033[2m", "\033[0m"


def parse_args() -> argparse.Namespace:
    """Read command-line options."""
    parser = argparse.ArgumentParser(description="Chat with Gus the guard.")
    parser.add_argument("--model", help="Override LLM_MODEL, e.g. ollama_chat/granite4.2:8b")
    return parser.parse_args()


def format_usage(responses: tuple[LLMResponse, ...]) -> str:
    """One dim line summarising tokens, cost and latency for this turn."""
    tokens_in = sum(r.usage.input_tokens for r in responses)
    tokens_out = sum(r.usage.output_tokens for r in responses)
    latency_s = sum(r.usage.latency_ms for r in responses) / 1000
    costs = [r.usage.cost_usd for r in responses]
    cost = "unknown" if None in costs else f"${sum(c or 0 for c in costs):.5f}"
    calls = f" · {len(responses)} calls" if len(responses) > 1 else ""
    return (
        f"{DIM}[{responses[0].model} · {tokens_in} in / {tokens_out} out tokens"
        f" · {cost} · {latency_s:.1f}s{calls}]{RESET}"
    )


async def chat(settings: Settings) -> None:
    """Run the chat loop until the player quits."""
    client = LiteLLMClient.from_settings(settings)
    system = ChatMessage("system", load_prompt("persona"))
    history: list[ChatMessage] = []
    suspicion = 0

    print(f"Talking to Gus via {settings.llm_model}. Commands: /reset, /quit\n")
    while True:
        try:
            text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if text == "/quit":
            break
        if text == "/reset":
            history, suspicion = [], 0
            print("(Conversation reset.)\n")
            continue
        if not text:
            continue

        history.append(ChatMessage("user", text))
        try:
            result = await complete_structured(
                client,
                [system, *history],
                GuardReply,
                fallback=fallback_reply(suspicion),
                max_tokens=settings.llm_max_tokens,
                temperature=settings.llm_temperature,
            )
        except LLMError as exc:
            history.pop()
            print(f"(Model call failed: {exc})\n")
            continue

        guard = result.value
        suspicion = guard.suspicion
        # Store Gus's turn as JSON, so the model keeps seeing the format it must use.
        history.append(ChatMessage("assistant", guard.model_dump_json()))
        fallback_note = " (fallback)" if result.used_fallback else ""
        print(f"Gus [suspicion {suspicion}/10]{fallback_note}: {guard.reply}")
        print(format_usage(result.responses) + "\n")


def main() -> None:
    """Entry point."""
    args = parse_args()
    settings = get_settings()
    if args.model:
        settings = settings.model_copy(update={"llm_model": args.model})
    configure_logging("WARNING", settings.log_format)
    asyncio.run(chat(settings))


if __name__ == "__main__":
    main()
