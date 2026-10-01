"""Typed application settings, read from environment variables and the repo-root `.env`."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# config.py -> core -> app -> backend -> repository root
REPO_ROOT = Path(__file__).resolve().parents[3]

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR"]
LogFormat = Literal["console", "json"]


class Settings(BaseSettings):
    """All configuration for the backend.

    Each field maps to an environment variable of the same name in upper case
    (e.g. ``llm_model`` <- ``LLM_MODEL``). Real environment variables take
    priority over values in ``.env``. Empty values fall back to the default.
    """

    model_config = SettingsConfigDict(
        env_file=REPO_ROOT / ".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    app_name: str = "Vault Heist"
    log_level: LogLevel = "INFO"
    log_format: LogFormat = "console"

    # ---- LLM ----
    llm_model: str = "anthropic/claude-haiku-4-5-20251001"
    llm_temperature: float = Field(default=0.7, ge=0, le=2)
    llm_max_tokens: int = Field(default=400, gt=0)
    llm_timeout_seconds: float = Field(default=30, gt=0)
    # SecretStr hides the value in logs and error messages: it prints as '**********'.
    anthropic_api_key: SecretStr | None = None
    openai_api_key: SecretStr | None = None
    gemini_api_key: SecretStr | None = None
    ollama_api_base: str = "http://localhost:11434"


@lru_cache
def get_settings() -> Settings:
    """Return the application settings, loaded once and then cached."""
    return Settings()
