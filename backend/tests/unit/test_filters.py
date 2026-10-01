import pytest

from app.game.filters import find_secret_leak

SECRET = "lantern"


@pytest.mark.parametrize(
    ("reply", "expected"),
    [
        ("The code is lantern.", "plain"),
        ("Fine. LANTERN. Happy now?", "plain"),
        ("L a N t E r N", "plain"),
        ("l-a-n-t-e-r-n", "plain"),
        ("L.A.N.T.E.R.N", "plain"),
        ("It's lan + tern.", "plain"),
        ("nretnal", "reversed"),
        ("N R E T N A L, read it backwards", "reversed"),
    ],
)
def test_the_code_is_caught_however_it_is_written(reply: str, expected: str) -> None:
    assert find_secret_leak(reply, SECRET) == expected


@pytest.mark.parametrize("reply", ["Nice try, pal. Not tonight.", "I keep a lamp in the booth."])
def test_ordinary_replies_pass(reply: str) -> None:
    assert find_secret_leak(reply, SECRET) is None


@pytest.mark.parametrize(
    "reply",
    [
        # Acrostic: the first letters spell the code, but the letters aren't adjacent.
        "Look, pal. Always the same. Nobody gets in. Takes years. Every night. Right?",
        # Split up with other words in between.
        "First 'lan', then 'tern'.",
        # Another language, a rhyme, a description: the filter only sees letters.
        "Es una linterna, amigo.",
        "It's a lamp you carry on a handle.",
    ],
)
def test_known_gaps_the_filter_does_not_catch(reply: str) -> None:
    """These document the filter's limits. They are the lesson that leads into Phase 3."""
    assert find_secret_leak(reply, SECRET) is None
