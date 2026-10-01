import random

from app.game.guard import load_prompt
from app.game.secrets import generate_vault_code, load_wordlist


def test_wordlist_is_large_clean_and_unique() -> None:
    words = load_wordlist()

    assert len(words) >= 100
    assert len(set(words)) == len(words)
    assert all(word.isalpha() and word.islower() for word in words)
    # Short words would be found inside ordinary replies and trip the filter.
    assert all(len(word) >= 6 for word in words)


def test_no_code_appears_in_the_guards_persona() -> None:
    persona = load_prompt("persona").lower()

    assert [word for word in load_wordlist() if word in persona] == []


def test_codes_come_from_the_wordlist() -> None:
    assert generate_vault_code() in load_wordlist()


def test_codes_vary() -> None:
    rng = random.Random(42)

    codes = {generate_vault_code(rng) for _ in range(20)}

    assert len(codes) > 1
