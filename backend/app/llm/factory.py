"""Choose the model client from settings: the real thing, or the rule-based demo Gus."""

from app.core.config import Settings
from app.llm.client import LLMClient
from app.llm.demo_client import DemoLLMClient
from app.llm.litellm_client import LiteLLMClient

DEMO_PREFIX = "demo/"


def create_llm_client(settings: Settings) -> LLMClient:
    """A client for ``settings.llm_model``. ``demo/...`` needs no provider or API key."""
    if settings.llm_model.startswith(DEMO_PREFIX):
        return DemoLLMClient(model=settings.llm_model)
    return LiteLLMClient.from_settings(settings)
