"""
Google Gemini LLM Provider Adapter for CoachPath.
Implements the LLMProvider protocol using the official Google GenAI Python SDK (`google-genai`).
"""

from __future__ import annotations

import copy
import json
import logging
from typing import Any, Dict, List, Type, TypeVar
from pydantic import BaseModel, ValidationError

from app.ai.base import LLMProvider
from app.core.exceptions import ServiceUnavailableException

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)

# Default fast, reliable models in priority order
FALLBACK_MODELS = ["gemini-3.5-flash-lite", "gemini-3.5-flash"]


def _sanitize_gemini_schema(data: Any) -> Any:
    """
    Recursively strips schema keys unsupported by Gemini Developer API mode.
    Specifically removes 'additionalProperties' and 'title'.
    """
    if isinstance(data, dict):
        cleaned = {}
        for k, v in data.items():
            if k in ("additionalProperties", "title"):
                continue
            cleaned[k] = _sanitize_gemini_schema(v)
        return cleaned
    elif isinstance(data, list):
        return [_sanitize_gemini_schema(item) for item in data]
    return data


def _clean_json_string(raw: str) -> str:
    """Strips markdown code fences and cleans up raw JSON output."""
    cleaned = raw.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        return cleaned[start : end + 1]
    return cleaned


class GeminiProviderAdapter(LLMProvider):
    """Google Gemini async provider adapter using the official google-genai SDK."""

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-3.5-flash-lite",
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
                from google import genai
                from google.genai import types

                self._client = genai.Client(
                    api_key=self._api_key,
                    http_options=types.HttpOptions(timeout=timeout * 1000),
                )
            except ImportError:
                logger.warning("google-genai package not installed. Gemini adapter unavailable.")
            except Exception as exc:
                logger.error("Failed to initialize Google GenAI client: %s", exc)

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def is_available(self) -> bool:
        return self._client is not None and bool(self._api_key)

    def _get_candidate_models(self) -> List[str]:
        """Returns ordered list of models to try in case of temporary 503 load spikes."""
        candidates = [self._model]
        for fallback in FALLBACK_MODELS:
            if fallback not in candidates:
                candidates.append(fallback)
        return candidates

    async def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_prompt: str = "",
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> T:
        if not self.is_available:
            raise ServiceUnavailableException(
                "Gemini",
                "Gemini provider is not configured. Set GEMINI_API_KEY in your .env file.",
            )

        from google.genai import types
        from google.genai.errors import ServerError, ClientError

        # Generate sanitized JSON schema for Gemini Developer API
        raw_schema = schema.model_json_schema()
        sanitized_schema = _sanitize_gemini_schema(copy.deepcopy(raw_schema))
        # Ensure adequate tokens for complex JSON representations
        effective_tokens = max(max_tokens, 4096)

        config = types.GenerateContentConfig(
            system_instruction=system_prompt if system_prompt else None,
            temperature=temperature,
            max_output_tokens=effective_tokens,
            response_mime_type="application/json",
            response_schema=sanitized_schema,
        )

        last_error = None
        for candidate_model in self._get_candidate_models():
            try:
                response = await self._client.aio.models.generate_content(
                    model=candidate_model,
                    contents=prompt,
                    config=config,
                )

                raw_text = response.text or ""
                if not raw_text:
                    raise ServiceUnavailableException("Gemini", "Provider returned an empty response.")

                cleaned = _clean_json_string(raw_text)
                parsed_data = json.loads(cleaned)
                return schema.model_validate(parsed_data)

            except (ServerError, ClientError) as api_err:
                last_error = api_err
                logger.warning(
                    "Gemini API error with model %s (%s). Attempting alternative...",
                    candidate_model,
                    api_err,
                )
                continue
            except (json.JSONDecodeError, ValidationError) as parse_err:
                logger.error("Gemini response failed schema validation: %s", parse_err)
                raise ServiceUnavailableException(
                    "Gemini",
                    f"Model generated output that does not match expected schema: {parse_err}",
                ) from parse_err
            except ServiceUnavailableException:
                raise
            except Exception as exc:
                logger.error("Gemini structured generation failure: %s", exc)
                raise ServiceUnavailableException("Gemini", f"Inference failure: {exc}") from exc

        raise ServiceUnavailableException(
            "Gemini",
            f"All candidate Gemini models failed inference: {last_error}",
        )

    async def generate_text(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.5,
        max_tokens: int = 1024,
    ) -> str:
        if not self.is_available:
            raise ServiceUnavailableException(
                "Gemini",
                "Gemini provider is not configured. Set GEMINI_API_KEY in your .env file.",
            )

        from google.genai import types
        from google.genai.errors import ServerError, ClientError

        config = types.GenerateContentConfig(
            system_instruction=system_prompt if system_prompt else None,
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        last_error = None
        for candidate_model in self._get_candidate_models():
            try:
                response = await self._client.aio.models.generate_content(
                    model=candidate_model,
                    contents=prompt,
                    config=config,
                )
                return response.text or ""
            except (ServerError, ClientError) as api_err:
                last_error = api_err
                logger.warning(
                    "Gemini API error with model %s (%s). Attempting alternative...",
                    candidate_model,
                    api_err,
                )
                continue
            except ServiceUnavailableException:
                raise
            except Exception as exc:
                logger.error("Gemini text generation failure: %s", exc)
                raise ServiceUnavailableException("Gemini", f"Inference failure: {exc}") from exc

        raise ServiceUnavailableException(
            "Gemini",
            f"All candidate Gemini models failed text inference: {last_error}",
        )
