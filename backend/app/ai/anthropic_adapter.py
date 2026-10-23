"""
Anthropic Claude LLM Provider Adapter for CoachPath.
Implements the LLMProvider protocol using the AsyncAnthropic client.
"""

from __future__ import annotations

import json
import logging
from typing import Type, TypeVar
from pydantic import BaseModel, ValidationError

from app.ai.base import LLMProvider
from app.core.exceptions import ServiceUnavailableException

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class AnthropicProviderAdapter(LLMProvider):
    """Anthropic Claude async provider adapter (supporting models like claude-3-haiku, claude-3-5-sonnet)."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-haiku-20240307",
        timeout: int = 30,
    ) -> None:
        self._api_key = api_key.strip() if api_key else ""
        self._model = model
        self._timeout = timeout
        self._client = None

        if self._api_key:
            try:
                import anthropic
                self._client = anthropic.AsyncAnthropic(
                    api_key=self._api_key,
                    timeout=timeout,
                )
            except ImportError:
                logger.warning("anthropic package not installed. Anthropic adapter unavailable.")

    @property
    def provider_name(self) -> str:
        return "anthropic"

    @property
    def is_available(self) -> bool:
        return self._client is not None and bool(self._api_key)

    async def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_prompt: str = "",
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> T:
        if not self.is_available:
            raise ServiceUnavailableException(
                "Anthropic",
                "Anthropic provider is not configured. Set ANTHROPIC_API_KEY in your .env file.",
            )

        schema_json = json.dumps(schema.model_json_schema())
        full_system = (
            f"{system_prompt}\n\nYou must respond exclusively with a valid JSON object matching this schema:\n{schema_json}"
            if system_prompt
            else f"You are a helpful assistant. Respond exclusively with a valid JSON object matching this schema:\n{schema_json}"
        )

        try:
            message = await self._client.messages.create(
                model=self._model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=full_system,
                messages=[{"role": "user", "content": prompt}],
            )
            raw_text = message.content[0].text
            # Extract JSON block if wrapped in markdown
            start = raw_text.find("{")
            end = raw_text.rfind("}") + 1
            if start >= 0 and end > start:
                raw_json = raw_text[start:end]
            else:
                raw_json = raw_text

            parsed = json.loads(raw_json)
            return schema.model_validate(parsed)
        except (json.JSONDecodeError, ValidationError) as parse_err:
            logger.error("Anthropic response failed schema validation: %s", parse_err)
            raise ServiceUnavailableException(
                "Anthropic",
                f"Model generated output that does not match expected schema: {parse_err}",
            ) from parse_err
        except Exception as exc:
            logger.error("Anthropic generation error: %s", exc)
            raise ServiceUnavailableException("Anthropic", f"Inference failure: {exc}") from exc

    async def generate_text(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.5,
        max_tokens: int = 1024,
    ) -> str:
        if not self.is_available:
            raise ServiceUnavailableException(
                "Anthropic",
                "Anthropic provider is not configured. Set ANTHROPIC_API_KEY in your .env file.",
            )

        try:
            message = await self._client.messages.create(
                model=self._model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or "You are a helpful assistant.",
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text
        except Exception as exc:
            logger.error("Anthropic text generation error: %s", exc)
            raise ServiceUnavailableException("Anthropic", f"Inference failure: {exc}") from exc
