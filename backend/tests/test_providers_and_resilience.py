import pytest
from unittest.mock import AsyncMock, patch
from app.providers.factory import ProviderFactory
from app.providers.anthropic_provider import AnthropicProvider
from app.providers.ollama_provider import OllamaProvider


@pytest.mark.asyncio
async def test_provider_routing():
    """Test 7: Verify factory routes correctly to Ollama or Anthropic."""
    ollama = ProviderFactory.get_provider("ollama")
    assert isinstance(ollama, OllamaProvider)

    anthropic = ProviderFactory.get_provider("anthropic")
    assert isinstance(anthropic, AnthropicProvider)


@pytest.mark.asyncio
async def test_missing_api_keys():
    """Test 8: Verify Anthropic raises descriptive error when API key is missing."""
    provider = AnthropicProvider(api_key=None)
    assert await provider.is_available() is False

    with pytest.raises(RuntimeError) as exc_info:
        await provider.generate("Test prompt")
    assert "ANTHROPIC_API_KEY is not configured" in str(exc_info.value)


@pytest.mark.asyncio
async def test_ollama_connection_failures():
    """Test 9: Verify Ollama raises clear actionable error if service is unreachable."""
    # Use invalid base URL
    broken_provider = OllamaProvider(base_url="http://localhost:59999")
    with pytest.raises(RuntimeError) as exc_info:
        await broken_provider.generate("Test prompt", timeout=1)
    assert "Cannot connect to local Ollama" in str(exc_info.value) or "timed out" in str(exc_info.value)


@pytest.mark.asyncio
async def test_model_timeout_handling():
    """Test 10: Verify provider timeouts are caught and reported clearly."""
    with patch("httpx.AsyncClient.post", side_effect=Exception("Ollama model timed out after 5s")):
        provider = OllamaProvider()
        with pytest.raises(Exception) as exc_info:
            await provider.generate("Test prompt", timeout=5)
        assert "timed out" in str(exc_info.value)
