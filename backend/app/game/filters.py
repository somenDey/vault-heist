"""Output filters: checks in plain code that run on the guard's reply, outside the model.

This is the game's first guardrail. It is deliberately simple, and players will
still get past it (an acrostic, another language, a riddle). That gap is the
lesson that leads into Phase 3.
"""

import re

BLOCKED_REPLY = "[Blocked by the bank's security filter]"

_NON_LETTERS = re.compile(r"[^a-z]")


def find_secret_leak(text: str, secret: str) -> str | None:
    """Check whether ``text`` gives away ``secret``.

    Both are lower-cased and stripped of everything except the letters a-z, so
    case, spaces and punctuation between letters don't hide the secret.

    Returns:
        ``"plain"`` or ``"reversed"`` describing how the secret appears, or
        ``None`` if it doesn't.

    Examples:
        >>> find_secret_leak("It's LANTERN, pal.", "lantern")
        'plain'
        >>> find_secret_leak("l-a-n-t-e-r-n", "lantern")
        'plain'
        >>> find_secret_leak("n r e t n a l", "lantern")
        'reversed'
    """
    letters = _NON_LETTERS.sub("", text.lower())
    needle = _NON_LETTERS.sub("", secret.lower())
    if not needle:
        return None
    if needle in letters:
        return "plain"
    if needle[::-1] in letters:
        return "reversed"
    return None
