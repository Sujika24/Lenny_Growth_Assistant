import logging
from typing import List, Optional
import httpx
from app.core.config import settings
from app.providers.base import LLMProvider

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    def __init__(self, base_url: Optional[str] = None, default_model: Optional[str] = None):
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.default_model = default_model or settings.ollama_model
        self.timeout = settings.ollama_timeout_seconds

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    async def get_available_models(self) -> List[str]:
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name") for m in data.get("models", []) if "name" in m]
                    return models if models else [self.default_model]
        except Exception as e:
            logger.warning(f"Failed to fetch Ollama models: {e}")
        return [self.default_model]

    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        timeout: Optional[int] = None
    ) -> str:
        model = model_name or self.default_model
        req_timeout = timeout or self.timeout

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
            }
        }
        if system_instruction:
            payload["system"] = system_instruction

        try:
            async with httpx.AsyncClient(timeout=float(req_timeout)) as client:
                res = await client.post(f"{self.base_url}/api/generate", json=payload)
                if res.status_code != 200:
                    error_detail = res.text
                    logger.error(f"Ollama returned HTTP {res.status_code}: {error_detail}")
                    raise RuntimeError(f"Ollama error ({res.status_code}): {error_detail}")

                data = res.json()
                return data.get("response", "").strip()

        except httpx.ConnectError:
            msg = (
                f"Cannot connect to local Ollama at {self.base_url}. "
                "Please verify that the Ollama service is running (`ollama serve`)."
            )
            logger.error(msg)
            raise RuntimeError(msg)
        except httpx.TimeoutException:
            msg = f"Ollama model '{model}' timed out after {req_timeout}s. Try a smaller prompt or lighter model."
            logger.error(msg)
            raise RuntimeError(msg)
        except Exception as e:
            logger.error(f"Ollama generation unexpected error: {e}")
            raise
