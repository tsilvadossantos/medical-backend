"""
LLM provider factory module.

Provides factory function to instantiate the configured LLM provider.
"""
import logging
from app.providers.base import LLMProvider
from app.core.settings import settings

logger = logging.getLogger(__name__)


def get_llm_provider() -> LLMProvider:
    """
    Get the configured LLM provider instance.

    Returns the appropriate provider based on LLM_PROVIDER setting.
    Defaults to Ollama if not specified.

    Returns:
        LLMProvider instance

    Raises:
        ValueError: If the configured provider is not supported
    """
    provider_name = settings.LLM_PROVIDER.lower()

    if provider_name == "ollama":
        from app.providers.ollama import OllamaProvider
        return OllamaProvider()

    elif provider_name == "openai":
        from app.providers.openai_provider import OpenAIProvider
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY required for OpenAI provider")
        return OpenAIProvider()

    elif provider_name == "anthropic":
        from app.providers.anthropic_provider import AnthropicProvider
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY required for Anthropic provider")
        return AnthropicProvider()

    else:
        raise ValueError(f"Unsupported LLM provider: {provider_name}")
