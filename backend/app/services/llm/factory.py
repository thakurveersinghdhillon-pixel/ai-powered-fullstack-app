from typing import Optional
from app.core.config import settings
from app.services.llm.base import BaseLLMProvider
from app.services.llm.openai_provider import OpenAIProvider
from app.services.llm.mock_provider import MockLLMProvider


def get_llm_provider(
    provider_override: Optional[str] = None,
    api_key_override: Optional[str] = None,
    model_override: Optional[str] = None,
) -> BaseLLMProvider:
    """
    Factory function returning the configured LLM provider instance.
    Defaults to OpenAIProvider when API key is configured, or MockLLMProvider
    when API key is absent for offline testing/verification.
    """
    provider_name = (provider_override or settings.LLM_PROVIDER).lower()
    api_key = api_key_override or settings.OPENAI_API_KEY

    if provider_name == "openai" and api_key:
        return OpenAIProvider(api_key=api_key, model=model_override)
    elif provider_name == "mock" or not api_key:
        return MockLLMProvider()
    else:
        return MockLLMProvider()
