# File: backend/providers/factory.py
from typing import Dict, Any
from .base import LLMProvider
from .anthropic_gateway import AnthropicGatewayProvider

DEFAULT_GATEWAY_URL = "http://localhost:3210"


class ProviderFactory:
    """Single transport: every agent talks to ClaudeMCP. ClaudeMCP fans out to
    Claude/Gemini/Ollama/LM Studio based on the model name we send."""

    _providers: Dict[str, LLMProvider] = {}

    @classmethod
    def get_provider(cls, engine_name: str, config: Dict[str, Any]) -> LLMProvider:
        base_url = config.get("gateway_url", DEFAULT_GATEWAY_URL)
        api_key = config.get("gateway_api_key", "")
        max_tokens = int(config.get("gateway_default_max_tokens", 4096))

        cache_key = f"{base_url}|{api_key}|{max_tokens}"
        if cache_key in cls._providers:
            return cls._providers[cache_key]

        provider = AnthropicGatewayProvider(base_url, api_key, default_max_tokens=max_tokens)
        cls._providers[cache_key] = provider
        return provider


provider_factory = ProviderFactory()
