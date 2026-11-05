"""Unit tests for the Anthropic adapter using a fake SDK client (no network)."""

from types import SimpleNamespace

import pytest
from pydantic import BaseModel

from app.ai.anthropic_adapter import AnthropicProviderAdapter
from app.core.exceptions import ServiceUnavailableException


class _Out(BaseModel):
    answer: str


class _FakeBetaMessages:
    def __init__(self, response):
        self.response = response
        self.calls = []

    async def parse(self, **kwargs):
        self.calls.append(kwargs)
        return self.response

    async def create(self, **kwargs):
        self.calls.append(kwargs)
        return self.response


def _adapter(response):
    adapter = AnthropicProviderAdapter(api_key="test-key", model="claude-opus-5-5")
    fake = _FakeBetaMessages(response)
    adapter._client = SimpleNamespace(beta=SimpleNamespace(messages=fake))
    return adapter, fake


@pytest.mark.asyncio
async def test_structured_returns_parsed_output_and_sends_current_api_shape():
    adapter, fake = _adapter(SimpleNamespace(stop_reason="end_turn", stop_details=None, parsed_output=_Out(answer="ok")))
    result = await adapter.generate_structured("q", _Out, system_prompt="sys", temperature=0.1, max_tokens=1024)
    assert result.answer == "ok"
    call = fake.calls[0]
    assert call["output_format"] is _Out
    assert "temperature" not in call
    assert call["max_tokens"] >= 16000
    assert call["fallbacks"] == "default"
    assert call["output_config"] == {"effort": "low"}


@pytest.mark.asyncio
async def test_text_joins_only_text_blocks():
    blocks = [SimpleNamespace(type="thinking", text=""), SimpleNamespace(type="text", text="hello")]
    adapter, _ = _adapter(SimpleNamespace(stop_reason="end_turn", stop_details=None, content=blocks))
    assert await adapter.generate_text("q") == "hello"


@pytest.mark.asyncio
async def test_refusal_raises_service_unavailable():
    adapter, _ = _adapter(SimpleNamespace(stop_reason="refusal", stop_details=SimpleNamespace(category="cyber"), parsed_output=None))
    with pytest.raises(ServiceUnavailableException):
        await adapter.generate_structured("q", _Out)


def test_unconfigured_adapter_is_unavailable():
    assert AnthropicProviderAdapter(api_key="").is_available is False
