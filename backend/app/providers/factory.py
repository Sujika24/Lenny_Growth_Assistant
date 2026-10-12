from typing import Dict, List
from app.core.config import settings
from app.providers.base import LLMProvider
from app.providers.ollama_provider import OllamaProvider
from app.providers.anthropic_provider import AnthropicProvider
from app.schemas.config import ProviderInfo


class ProviderFactory:
    _providers: Dict[str, LLMProvider] = {}

    @classmethod
    def get_provider(cls, name: str = None) -> LLMProvider:
        provider_name = (name or settings.default_provider).lower()
        if provider_name == "anthropic":
            if "anthropic" not in cls._providers:
                cls._providers["anthropic"] = AnthropicProvider()
            return cls._providers["anthropic"]
        else:
            # Default to Ollama
            if "ollama" not in cls._providers:
                cls._providers["ollama"] = OllamaProvider()
            return cls._providers["ollama"]

    @classmethod
    async def get_providers_info(cls) -> List[ProviderInfo]:
        ollama = cls.get_provider("ollama")
        anthropic = cls.get_provider("anthropic")

        ollama_avail = await ollama.is_available()
        ollama_models = await ollama.get_available_models() if ollama_avail else [settings.ollama_model]

        anthropic_avail = await anthropic.is_available()
        anthropic_models = await anthropic.get_available_models()

        return [
            ProviderInfo(
                id="ollama",
                name="Local Ollama",
                is_available=ollama_avail,
                models=ollama_models,
                default_model=settings.ollama_model,
                description="Runs 100% locally on your machine with zero cloud API keys."
            ),
            ProviderInfo(
                id="anthropic",
                name="Anthropic Claude",
                is_available=anthropic_avail,
                models=anthropic_models,
                default_model=settings.anthropic_model,
                description="Cloud AI via Anthropic Claude Agent SDK (requires ANTHROPIC_API_KEY)."
            )
        ]
