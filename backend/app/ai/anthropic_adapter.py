"""
Anthropic Claude LLM Provider Adapter for CoachPath.
Implements the LLMProvider protocol using the AsyncAnthropic client with
native structured outputs (validated against the caller's Pydantic schema).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Type, TypeVar
from pydantic import BaseModel

from app.ai.base import LLMProvider
from app.core.exceptions import ServiceUnavailableException

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)

# Thinking tokens count against max_tokens on current Claude models, so callers' small
# budgets (1-2k) would truncate output; this floor leaves room for thinking + the answer.
_MIN_MAX_TOKENS = 16000
# Server-side refusal fallback: the API re-runs a declined request on a suitable model.
_FALLBACK_BETA = "server-side-fallback-2026-07-01"


class AnthropicProviderAdapter(LLMProvider):
    """Anthropic Claude async provider adapter."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-opus-5-5",
        timeout: int = 30,
        max_retries: int = 2,
        effort: str = "low",
    ) -> None:
        self._api_key = api_key.strip() if api_key else ""
        self._model = model
        self._effort = effort
        self._client = None

        if self._api_key:
            try:
                import anthropic
                self._client = anthropic.AsyncAnthropic(
                    api_key=self._api_key,
                    timeout=float(timeout),
                    max_retries=max_retries,
                )
            except ImportError:
                logger.warning("anthropic package not installed. Anthropic adapter unavailable.")

    @property
    def provider_name(self) -> str:
        return "anthropic"

    @property
    def is_available(self) -> bool:
        return self._client is not None and bool(self._api_key)

    def _require_available(self) -> None:
        if not self.is_available:
            raise ServiceUnavailableException(
                "Anthropic",
                "Anthropic provider is not configured. Set ANTHROPIC_API_KEY in your .env file.",
            )

    def _request_kwargs(self, prompt: str, system_prompt: str, max_tokens: int) -> Dict[str, Any]:
        # temperature is intentionally not sent: current Claude models reject sampling params.
        return {
            "model": self._model,
            "max_tokens": max(max_tokens, _MIN_MAX_TOKENS),
            "system": system_prompt or "You are a helpful assistant.",
            "messages": [{"role": "user", "content": prompt}],
            "output_config": {"effort": self._effort},
            "betas": [_FALLBACK_BETA],
            "fallbacks": "default",
        }

    @staticmethod
    def _check_stop_reason(message: Any) -> None:
        if message.stop_reason == "refusal":
            category = getattr(message.stop_details, "category", None) if message.stop_details else None
            raise ServiceUnavailableException("Anthropic", f"Model declined the request (category: {category}).")
        if message.stop_reason == "max_tokens":
            raise ServiceUnavailableException("Anthropic", "Model output was truncated (max_tokens reached).")

    async def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_prompt: str = "",
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> T:
        self._require_available()
        import anthropic

        try:
            message = await self._client.beta.messages.parse(
                **self._request_kwargs(prompt, system_prompt, max_tokens),
                output_format=schema,
            )
        except anthropic.APIError as exc:
            logger.error("Anthropic generation error: %s", exc)
            raise ServiceUnavailableException("Anthropic", f"Inference failure: {exc}") from exc
        except Exception as exc:  # SDK raises on output that fails client-side schema validation
            logger.error("Anthropic response failed schema validation: %s", exc)
            raise ServiceUnavailableException(
                "Anthropic", f"Model generated output that does not match expected schema: {exc}"
            ) from exc

        self._check_stop_reason(message)
        if message.parsed_output is None:
            raise ServiceUnavailableException("Anthropic", "Model returned no structured output.")
        return message.parsed_output

    async def generate_text(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.5,
        max_tokens: int = 1024,
    ) -> str:
        self._require_available()
        import anthropic

        try:
            message = await self._client.beta.messages.create(
                **self._request_kwargs(prompt, system_prompt, max_tokens),
            )
        except anthropic.APIError as exc:
            logger.error("Anthropic text generation error: %s", exc)
            raise ServiceUnavailableException("Anthropic", f"Inference failure: {exc}") from exc

        self._check_stop_reason(message)
        return "".join(b.text for b in message.content if b.type == "text")
