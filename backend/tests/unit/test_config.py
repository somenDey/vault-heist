import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_environment_variable_overrides_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_MODEL", "openai/gpt-test")

    assert Settings(_env_file=None).llm_model == "openai/gpt-test"


def test_empty_value_falls_back_to_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_LEVEL", "")

    assert Settings(_env_file=None).log_level == "INFO"


def test_invalid_value_fails_at_startup(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_LEVEL", "LOUD")

    with pytest.raises(ValidationError):
        Settings(_env_file=None)
