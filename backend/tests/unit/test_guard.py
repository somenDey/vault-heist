import pytest
from pydantic import ValidationError

from app.game.guard import GuardReply, fallback_reply, load_prompt


def test_persona_prompt_loads_and_describes_the_reply_format() -> None:
    prompt = load_prompt("persona")

    assert "Gus" in prompt
    assert '"suspicion"' in prompt


@pytest.mark.parametrize("suspicion", [-1, 11])
def test_suspicion_must_be_between_0_and_10(suspicion: int) -> None:
    with pytest.raises(ValidationError):
        GuardReply(reply="Hi", suspicion=suspicion)


def test_fallback_keeps_the_current_suspicion() -> None:
    assert fallback_reply(7).suspicion == 7
