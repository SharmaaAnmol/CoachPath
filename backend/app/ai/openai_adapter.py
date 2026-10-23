"""
OpenAI LLM Provider Adapter for CoachPath.
Implements the LLMProvider protocol using the AsyncOpenAI client.
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


class OpenAIProviderAdapter(LLMProvider):
    """OpenAI async provider adapter (supporting models like gpt-4o-mini, gpt-4o)."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        timeout: int = 30,
        max_retries: int = 2,
    ) -> None:
        self._api_key = api_key.strip() if api_key else ""
        self._model = model
        self._timeout = timeout
        self._max_retries = max_retries
        self._client = None

        if self._api_key:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(
                    api_key=self._api_key,
                    timeout=timeout,
                    max_retries=max_retries,
                )
            except ImportError:
                logger.warning("openai package not installed. OpenAI adapter unavailable.")

    @property
    def provider_name(self) -> str:
        return "openai"

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
                "OpenAI",
                "OpenAI provider is not configured. Set OPENAI_API_KEY in your .env file.",
            )

        messages = []
        schema_json = json.dumps(schema.model_json_schema())
        sys_instruction = (
            f"{system_prompt}\n\nYou must return a valid JSON object matching this schema:\n{schema_json}"
            if system_prompt
            else f"You are a helpful assistant. Return a valid JSON object matching this schema:\n{schema_json}"
        )
        messages.append({"role": "system", "content": sys_instruction})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"},
            )
            raw_content = response.choices[0].message.content
            if not raw_content:
                raise ServiceUnavailableException("OpenAI", "Provider returned an empty response.")
            parsed = json.loads(raw_content)
            return schema.model_validate(parsed)
        except (json.JSONDecodeError, ValidationError) as parse_err:
            logger.error("OpenAI response failed schema validation: %s", parse_err)
            raise ServiceUnavailableException(
                "OpenAI",
                f"Model generated output that does not match expected schema: {parse_err}",
            ) from parse_err
        except Exception as exc:
            logger.error("OpenAI generation error: %s", exc)
            raise ServiceUnavailableException("OpenAI", f"Inference failure: {exc}") from exc

    async def generate_text(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.5,
        max_tokens: int = 1024,
    ) -> str:
        if not self.is_available:
            raise ServiceUnavailableException(
                "OpenAI",
                "OpenAI provider is not configured. Set OPENAI_API_KEY in your .env file.",
            )

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            logger.error("OpenAI text generation error: %s", exc)
            raise ServiceUnavailableException("OpenAI", f"Inference failure: {exc}") from exc
