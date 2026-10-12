from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class LLMProvider(ABC):
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        timeout: Optional[int] = None
    ) -> str:
        """Generates text from the underlying LLM."""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Checks if the provider service is reachable."""
        pass

    @abstractmethod
    async def get_available_models(self) -> List[str]:
        """Returns list of models available under this provider."""
        pass
