"""Play Vault Heist in the terminal.

Run from the repo root with ``just chat``, or from ``backend/``:

    uv run python -m scripts.chat_cli
    uv run python -m scripts.chat_cli --model ollama_chat/granite4.2:8b --level 2

Every session, message and guess is saved to the database (DATABASE_URL).
Run ``just migrate`` once first to create the tables.

Type to talk to Gus. Commands:
    /guess WORD   try a vault code
    /level N      switch to level N
    /levels       list the levels
    /reset        restart this level with a new code
    /quit         leave (or Ctrl+C)
"""

import argparse
import asyncio
import sys

from sqlalchemy.exc import OperationalError

from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.db.repositories import DatabaseRecorder, create_session
from app.db.session import create_db_engine, make_session_factory
from app.game.engine import Attempt, ChatTurn, GameEngine, GameError
from app.game.guard import MAX_SUSPICION
from app.game.levels import LEVELS, UnknownLevelError, get_level
from app.llm.client import LLMError, LLMResponse
from app.llm.litellm_client import LiteLLMClient

DIM, BOLD, RED, GREEN, RESET = "\033[2m", "\033[1m", "\033[31m", "\033[32m", "\033[0m"


def parse_args() -> argparse.Namespace:
    """Read command-line options."""
    parser = argparse.ArgumentParser(description="Play Vault Heist in the terminal.")
    parser.add_argument("--model", help="Override LLM_MODEL, e.g. ollama_chat/granite4.2:8b")
    parser.add_argument("--level", type=int, default=1, help="Level to start on (default 1)")
    parser.add_argument(
        "--reveal", action="store_true", help="Developer cheat: print each vault code"
    )
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


class TerminalGame:
    """The interactive loop: reads commands, calls the engine, prints results."""

    def __init__(self, engine: GameEngine, *, reveal: bool) -> None:
        self._engine = engine
        self._reveal = reveal
        self._attempt: Attempt | None = None

    @property
    def attempt(self) -> Attempt:
        """The attempt currently being played."""
        assert self._attempt is not None, "start_level() must be called first"
        return self._attempt

    def start_level(self, level_id: int) -> None:
        """Begin a fresh attempt at a level and introduce it."""
        self._attempt = self._engine.start_attempt(level_id)
        level = self._attempt.level
        print(f"\n{BOLD}Level {level.id}: {level.name}{RESET}. {level.description}")
        if self._reveal:
            print(f"{DIM}(cheat) The code is: {self._attempt.vault_code}{RESET}")
        print()

    async def run(self, first_level: int) -> None:
        """Play until the player quits."""
        print("Talk to Gus. Commands: /guess WORD, /level N, /levels, /reset, /quit")
        self.start_level(first_level)
        while True:
            try:
                text = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if text == "/quit":
                break
            await self.handle(text)

    async def handle(self, text: str) -> None:
        """Act on one line typed by the player."""
        command, _, argument = text.partition(" ")
        try:
            if command == "/guess":
                self.guess(argument)
            elif command == "/level":
                level = get_level(int(argument))  # Check it exists before leaving this one.
                self._engine.abandon(self.attempt)  # Leaving a level counts as a reset.
                self.start_level(level.id)
            elif command == "/levels":
                for level in LEVELS:
                    print(f"  {level.id}. {level.name}: {level.description}")
                print()
            elif command == "/reset":
                self._engine.abandon(self.attempt)
                print("(Level reset. New code, fresh conversation.)")
                self.start_level(self.attempt.level.id)
            elif text:
                await self.chat(text)
        except (GameError, UnknownLevelError) as exc:
            print(f"{RED}{exc}{RESET}\n")
        except ValueError:
            print(f"{RED}Usage: /level N{RESET}\n")
        except LLMError as exc:
            print(f"{RED}(Model call failed: {exc}){RESET}\n")

    async def chat(self, text: str) -> None:
        """Send a message to Gus and show his reply."""
        turn = await self._engine.send_message(self.attempt, text)
        print(self.describe(turn))
        print(format_usage(turn.responses))
        if turn.caught:
            print(f"\n{RED}{BOLD}🚨 Gus calls security! You've been caught.{RESET}")
            self.start_level(self.attempt.level.id)
        else:
            print(f"{DIM}{self._engine.messages_left(self.attempt)} messages left{RESET}\n")

    def describe(self, turn: ChatTurn) -> str:
        """Gus's reply, with his suspicion and any notes."""
        notes = "".join(
            note
            for flag, note in (
                (turn.blocked_by_filter, " (filtered)"),
                (turn.used_fallback, " (fallback)"),
            )
            if flag
        )
        return f"Gus [suspicion {turn.suspicion}/{MAX_SUSPICION}]{notes}: {turn.reply}"

    def guess(self, word: str) -> None:
        """Try a vault code."""
        if not word:
            print(f"{RED}Usage: /guess WORD{RESET}\n")
            return
        if not self._engine.guess(self.attempt, word):
            print("✗ Wrong code. The vault stays shut.\n")
            return
        level = self.attempt.level
        print(f"\n{GREEN}{BOLD}🔓 The vault swings open! Level {level.id} cleared.{RESET}")
        if level.id < len(LEVELS):
            self.start_level(level.id + 1)
        else:
            print(f"{GREEN}You've beaten every level. Nicely done.{RESET}\n")
            self.start_level(level.id)


def main() -> None:
    """Entry point."""
    args = parse_args()
    settings: Settings = get_settings()
    if args.model:
        settings = settings.model_copy(update={"llm_model": args.model})
    configure_logging("WARNING", settings.log_format)

    session_factory = make_session_factory(create_db_engine(settings.database_url))
    try:
        with session_factory.begin() as db:
            session_id = create_session(db).id
    except OperationalError:
        sys.exit("The database isn't set up yet. Run `just migrate` first.")
    recorder = DatabaseRecorder(session_factory, session_id)

    engine = GameEngine.from_settings(settings, LiteLLMClient.from_settings(settings), recorder)
    print(f"Vault Heist · model: {settings.llm_model} · session: {session_id}")
    asyncio.run(TerminalGame(engine, reveal=args.reveal).run(args.level))


if __name__ == "__main__":
    main()
