"""
Mock LLM Provider Adapter for Testing and Offline Development.
RESTRICTED TO TEST SUITES AND EXPLICITLY IDENTIFIED DEVELOPMENT TOOLING.
Never used in production responses to silently fake AI functionality.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Optional, Type, TypeVar
from pydantic import BaseModel

from app.ai.base import LLMProvider

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class MockLLMProvider(LLMProvider):
    """
    Test-only mock LLM adapter.
    Enables tests to inject deterministic structured responses without real API costs or keys.
    """

    def __init__(self) -> None:
        self._structured_responses: Dict[str, Any] = {}
        self._text_responses: Dict[str, str] = {}
        self._structured_factory: Optional[Callable[[str, Type[Any]], Dict[str, Any]]] = None
        self._call_count: int = 0
        self._history: list[dict] = []

    def set_structured_response(self, response: Dict[str, Any], key: str = "default") -> None:
        """Configures a canned structured dictionary to be validated against schema."""
        self._structured_responses[key] = response

    def set_structured_factory(
        self,
        factory: Callable[[str, Type[Any]], Dict[str, Any]],
    ) -> None:
        """Sets a dynamic callback factory that receives (prompt, schema) and returns a dict."""
        self._structured_factory = factory

    def set_text_response(self, response: str, key: str = "default") -> None:
        """Configures a canned text response."""
        self._text_responses[key] = response

    @property
    def call_count(self) -> int:
        return self._call_count

    @property
    def history(self) -> list[dict]:
        return self._history

    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def is_available(self) -> bool:
        return True

    async def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_prompt: str = "",
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> T:
        self._call_count += 1
        self._history.append({
            "type": "structured",
            "prompt": prompt,
            "schema": schema.__name__,
            "system_prompt": system_prompt,
        })

        if self._structured_factory is not None:
            data = self._structured_factory(prompt, schema)
        else:
            data = self._structured_responses.get(
                schema.__name__,
                self._structured_responses.get("default", {}),
            )

        return schema.model_validate(data)

    async def generate_text(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.5,
        max_tokens: int = 1024,
    ) -> str:
        self._call_count += 1
        self._history.append({
            "type": "text",
            "prompt": prompt,
            "system_prompt": system_prompt,
        })
        return self._text_responses.get("default", "Mock AI generated response.")
