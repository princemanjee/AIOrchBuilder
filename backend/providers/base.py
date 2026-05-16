# File: backend/providers/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = "", model: Optional[str] = None, **kwargs) -> str:
        """Generates a response from the LLM."""
        pass

    @abstractmethod
    def name(self) -> str:
        """Returns the name of the provider."""
        pass
