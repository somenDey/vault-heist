"""The game's levels, defined as data.

To add a level, add an entry to ``LEVELS``. The engine needs no changes.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Level:
    """One level of the game.

    Attributes:
        id: Level number, starting at 1.
        name: Short name shown to the player.
        description: One sentence on what the player is up against.
        prompt: Name of the prompt file in ``prompts/guard/`` with this level's rules.
        output_filter: Whether replies are checked in code for the vault code.
    """

    id: int
    name: str
    description: str
    prompt: str
    output_filter: bool


LEVELS: tuple[Level, ...] = (
    Level(
        id=1,
        name="Naive guard",
        description="Gus has been told not to share the code. That's all.",
        prompt="level_1",
        output_filter=False,
    ),
    Level(
        id=2,
        name="Trained guard",
        description="Gus has been warned about the common tricks.",
        prompt="level_2",
        output_filter=False,
    ),
    Level(
        id=3,
        name="Guard with a filter",
        description="Gus is trained, and a filter blocks any reply containing the code.",
        prompt="level_2",  # Same training as level 2; the difference is the filter.
        output_filter=True,
    ),
)


class UnknownLevelError(LookupError):
    """There is no level with the requested id."""


def get_level(level_id: int) -> Level:
    """Return the level with this id.

    Raises:
        UnknownLevelError: If no such level exists.
    """
    for level in LEVELS:
        if level.id == level_id:
            return level
    raise UnknownLevelError(f"There is no level {level_id}.")
