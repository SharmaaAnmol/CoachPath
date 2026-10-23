"""
AI Provider Factory for CoachPath.
Instantiates the configured LLMProvider based on application settings.
Never silently replaces an unconfigured provider with a mock in production.
"""

from __future__ import annotations

import logging
from typing import Optional

from app.ai.base import LLMProvider
from app.core.config import settings

logger = logging.getLogger(__name__)

_provider_instance: Optional[LLMProvider] = None


def create_llm_provider(provider_override: Optional[str] = None) -> LLMProvider:
    """
    Instantiates and returns the configured LLM provider.
    If provider credentials are missing, returns an adapter whose is_available is False,
    which will raise ServiceUnavailableException if invoked.
    """
    provider = provider_override or settings.AI_PROVIDER

    if provider == "gemini":
        from app.ai.gemini_adapter import GeminiProviderAdapter
        adapter = GeminiProviderAdapter(
            api_key=settings.GEMINI_API_KEY,
            model=settings.GEMINI_MODEL,
            timeout=settings.AI_REQUEST_TIMEOUT,
            max_retries=settings.AI_MAX_RETRIES,
        )
        if not adapter.is_available:
            logger.info(
                "Gemini provider selected but GEMINI_API_KEY is not set. "
                "AI calls will return ServiceUnavailableException (503) until key is provided."
            )
        return adapter

    elif provider == "groq":
        from app.ai.groq_adapter import GroqProviderAdapter
        adapter = GroqProviderAdapter(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL,
            timeout=settings.AI_REQUEST_TIMEOUT,
            max_retries=settings.AI_MAX_RETRIES,
        )
        if not adapter.is_available:
            logger.info(
                "Groq provider selected but GROQ_API_KEY is not set. "
                "AI calls will return ServiceUnavailableException (503) until key is provided."
            )
        return adapter

    elif provider == "openai":
        from app.ai.openai_adapter import OpenAIProviderAdapter
        adapter = OpenAIProviderAdapter(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL,
            timeout=settings.AI_REQUEST_TIMEOUT,
            max_retries=settings.AI_MAX_RETRIES,
        )
        if not adapter.is_available:
            logger.info(
                "OpenAI provider selected but OPENAI_API_KEY is not set. "
                "AI calls will return ServiceUnavailableException (503) until key is provided."
            )
        return adapter

    elif provider == "anthropic":
        from app.ai.anthropic_adapter import AnthropicProviderAdapter
        adapter = AnthropicProviderAdapter(
            api_key=settings.ANTHROPIC_API_KEY,
            model=settings.ANTHROPIC_MODEL,
            timeout=settings.AI_REQUEST_TIMEOUT,
        )
        if not adapter.is_available:
            logger.info(
                "Anthropic provider selected but ANTHROPIC_API_KEY is not set. "
                "AI calls will return ServiceUnavailableException (503) until key is provided."
            )
        return adapter

    elif provider == "disabled":
        from app.ai.gemini_adapter import GeminiProviderAdapter
        return GeminiProviderAdapter(api_key="", model=settings.GEMINI_MODEL)

    else:
        logger.warning("Unrecognized AI_PROVIDER '%s'. Defaulting to unconfigured Gemini adapter.", provider)
        from app.ai.gemini_adapter import GeminiProviderAdapter
        return GeminiProviderAdapter(api_key="", model=settings.GEMINI_MODEL)


def get_llm_provider() -> LLMProvider:
    """Returns the singleton LLM provider instance, creating it on first access."""
    global _provider_instance
    if _provider_instance is None:
        _provider_instance = create_llm_provider()
    return _provider_instance


def override_llm_provider(provider: LLMProvider) -> None:
    """
    Overrides the singleton LLM provider.
    FOR TEST SUITES ONLY. Always call reset_llm_provider() in test teardown.
    """
    global _provider_instance
    _provider_instance = provider


def reset_llm_provider() -> None:
    """Clears the singleton so the next call recreates the configured provider."""
    global _provider_instance
    _provider_instance = None
