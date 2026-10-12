import logging
from typing import List, Optional
from app.core.config import settings
from app.providers.base import LLMProvider

logger = logging.getLogger(__name__)


class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, default_model: Optional[str] = None):
        self.api_key = api_key or settings.anthropic_api_key
        self.default_model = default_model or settings.anthropic_model
        self.models = [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
        ]

    async def is_available(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 10)

    async def get_available_models(self) -> List[str]:
        return self.models

    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        timeout: Optional[int] = None
    ) -> str:
        if not await self.is_available():
            raise RuntimeError(
                "Anthropic Cloud Provider is selected, but ANTHROPIC_API_KEY is not configured. "
                "Please set ANTHROPIC_API_KEY in your environment or switch to Local Ollama."
            )

        try:
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=self.api_key, timeout=float(timeout or 60))
            model = model_name or self.default_model

            response = await client.messages.create(
                model=model,
                max_tokens=4096,
                temperature=temperature,
                system=system_instruction or "You are an expert product management and growth assistant.",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic generation error: {e}")
            raise
