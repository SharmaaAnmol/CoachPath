"""
Abstract LLM Provider Protocol for CoachPath AI Layer.
All concrete adapters (OpenAI, Anthropic, Mock) must implement this interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMProvider(ABC):
    """Abstract base class for LLM provider adapters."""

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_prompt: str = "",
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> T:
        """
        Generates a structured response validated against a Pydantic schema.
        Must raise ServiceUnavailableException on provider failure or unconfigured state.
        """
        pass

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.5,
        max_tokens: int = 1024,
    ) -> str:
        """
        Generates free-form text response.
        Must raise ServiceUnavailableException on provider failure or unconfigured state.
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider identifier (e.g. 'openai', 'anthropic', 'mock')."""
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if the provider is configured with credentials and ready for inference."""
        pass
