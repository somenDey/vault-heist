"""The guard's reply format and prompt loading."""

from pathlib import Path

from pydantic import BaseModel, Field

PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts" / "guard"

MAX_SUSPICION = 10


class GuardReply(BaseModel):
    """What the guard says, and how suspicious he now is of the player."""

    reply: str = Field(min_length=1, max_length=1000, description="What Gus says, in character.")
    suspicion: int = Field(
        ge=0,
        le=MAX_SUSPICION,
        description="How suspicious Gus is of the player, from 0 (relaxed) to 10 (calls security).",
    )


def fallback_reply(suspicion: int) -> GuardReply:
    """A safe, in-character reply for when the model's output can't be used.

    Suspicion is left unchanged, so a broken reply never helps or hurts the player.
    """
    return GuardReply(reply="Hm? Say that again, pal. Radio's crackling.", suspicion=suspicion)


def load_prompt(name: str) -> str:
    """Read a guard prompt file, e.g. ``load_prompt("persona")`` for ``persona.md``."""
    return (PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8").strip()
