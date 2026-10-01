import pytest

from app.game.guard import PROMPTS_DIR, VAULT_CODE_PLACEHOLDER
from app.game.levels import LEVELS, Level, UnknownLevelError, get_level


def test_there_are_three_levels_numbered_from_one() -> None:
    assert [level.id for level in LEVELS] == [1, 2, 3]


def test_only_level_three_uses_the_output_filter() -> None:
    assert [level.output_filter for level in LEVELS] == [False, False, True]


@pytest.mark.parametrize("level", LEVELS, ids=lambda level: f"level-{level.id}")
def test_every_level_prompt_exists_and_has_a_place_for_the_code(level: Level) -> None:
    prompt = (PROMPTS_DIR / f"{level.prompt}.md").read_text(encoding="utf-8")

    assert VAULT_CODE_PLACEHOLDER in prompt


def test_unknown_level_is_rejected() -> None:
    with pytest.raises(UnknownLevelError):
        get_level(99)
