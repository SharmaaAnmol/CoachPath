"""
Unit & Integration Tests for Google Gemini AI Provider Adapter.
Verifies client initialization, availability states, schema sanitization,
JSON cleanup, factory routing, and error behavior.
"""

import pytest
from pydantic import BaseModel, Field

from app.ai.base import LLMProvider
from app.ai.factory import create_llm_provider, get_llm_provider
from app.ai.gemini_adapter import (
    GeminiProviderAdapter,
    _clean_json_string,
    _sanitize_gemini_schema,
)
from app.core.exceptions import ServiceUnavailableException


class MockSchema(BaseModel):
    name: str = Field(description="Candidate name")
    skills: list[str] = Field(default_factory=list)


def test_gemini_adapter_unconfigured_availability():
    """Unconfigured Gemini adapter has is_available=False."""
    adapter = GeminiProviderAdapter(api_key="", model="gemini-3.5-flash-lite")
    assert adapter.provider_name == "gemini"
    assert adapter.is_available is False


@pytest.mark.asyncio
async def test_gemini_adapter_unconfigured_raises_503():
    """Calling generate_text on unconfigured adapter raises ServiceUnavailableException."""
    adapter = GeminiProviderAdapter(api_key="", model="gemini-3.5-flash-lite")
    with pytest.raises(ServiceUnavailableException) as exc_info:
        await adapter.generate_text("Hello")
    assert "Gemini provider is not configured" in str(exc_info.value)


@pytest.mark.asyncio
async def test_gemini_adapter_unconfigured_structured_raises_503():
    """Calling generate_structured on unconfigured adapter raises ServiceUnavailableException."""
    adapter = GeminiProviderAdapter(api_key="", model="gemini-3.5-flash-lite")
    with pytest.raises(ServiceUnavailableException) as exc_info:
        await adapter.generate_structured("Extract info", MockSchema)
    assert "Gemini provider is not configured" in str(exc_info.value)


def test_factory_creates_gemini_provider():
    """Factory creates a GeminiProviderAdapter when provider is 'gemini'."""
    provider = create_llm_provider(provider_override="gemini")
    assert isinstance(provider, GeminiProviderAdapter)
    assert provider.provider_name == "gemini"


def test_sanitize_gemini_schema_strips_additional_properties():
    """Schema sanitizer strips additionalProperties and title for Gemini Developer API mode."""
    raw_schema = {
        "title": "RootModel",
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "sub": {
                "title": "SubModel",
                "type": "object",
                "additionalProperties": True,
                "properties": {
                    "field": {"type": "string", "title": "FieldTitle"}
                },
            }
        },
    }
    cleaned = _sanitize_gemini_schema(raw_schema)
    assert "additionalProperties" not in str(cleaned)
    assert "title" not in str(cleaned)
    assert cleaned["properties"]["sub"]["properties"]["field"]["type"] == "string"


def test_clean_json_string():
    """JSON cleaner strips markdown code fences and outer prose."""
    fenced = "```json\n{\"status\": \"ok\"}\n```"
    assert _clean_json_string(fenced) == '{"status": "ok"}'

    with_prose = "Here is your JSON output:\n{\"status\": \"ok\"}\nHope this helps!"
    assert _clean_json_string(with_prose) == '{"status": "ok"}'
