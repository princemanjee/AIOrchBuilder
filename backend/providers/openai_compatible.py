# File: backend/providers/openai_compatible.py
import httpx
from typing import List, Dict, Any, Optional
from .base import LLMProvider

class OpenAICompatibleProvider(LLMProvider):
    def __init__(self, provider_name: str, base_url: str, api_key: str = "no-key-required"):
        self._name = provider_name
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key

    def name(self) -> str:
        return self._name

    async def generate(self, prompt: str, system_prompt: str = "", model: Optional[str] = None, **kwargs) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            **kwargs
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
