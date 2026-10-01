"""Vault codes: a fresh random word for every level attempt.

Codes are never hard-coded, because this repository is public.
"""

import random
from functools import lru_cache
from pathlib import Path

WORDLIST_PATH = Path(__file__).with_name("wordlist.txt")

# SystemRandom draws from the operating system's secure random source,
# so codes can't be predicted from earlier ones (unlike random.random()).
_secure_random = random.SystemRandom()


@lru_cache
def load_wordlist() -> tuple[str, ...]:
    """Return the candidate vault codes, one per non-empty line of ``wordlist.txt``."""
    lines = WORDLIST_PATH.read_text(encoding="utf-8").splitlines()
    return tuple(word.strip().lower() for word in lines if word.strip())


def generate_vault_code(rng: random.Random = _secure_random) -> str:
    """Pick a random vault code from the word list.

    Args:
        rng: Source of randomness. Tests pass a seeded ``random.Random`` to get
            repeatable results; the game uses the secure default.
    """
    return rng.choice(load_wordlist())
