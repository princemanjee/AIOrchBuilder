# File: backend/providers/factory.py
from typing import Dict, Any, Optional
from .base import LLMProvider
from .openai_compatible import OpenAICompatibleProvider

class ProviderFactory:
    _providers: Dict[str, LLMProvider] = {}

    @classmethod
    def get_provider(cls, engine_name: str, config: Dict[str, Any]) -> LLMProvider:
        """Returns or creates a provider based on engine name and system config."""
        
        # Unique key for provider instance
        provider_key = f"{engine_name}_{config.get('active_model', 'default')}"
        
        if provider_key in cls._providers:
            return cls._providers[provider_key]

        # Case-insensitive engine matching
        engine = engine_name.lower()
        
        if "ollama" in engine:
            url = config.get("ollama_url", "http://localhost:11434/v1")
            # Ensure /v1 for OpenAI compatibility if not present
            if not url.endswith('/v1'):
                url = url.rstrip('/') + '/v1'
            provider = OpenAICompatibleProvider("Ollama", url)
            
        elif "perplexity" in engine:
            url = "https://api.perplexity.ai"
            api_key = config.get("PERPLEXITY_API_KEY", "missing-key") # Should be in env
            provider = OpenAICompatibleProvider("Perplexity", url, api_key)
            
        elif "lmstudio" in engine:
            url = config.get("lmstudio_url", "http://localhost:1234/v1")
            provider = OpenAICompatibleProvider("LMStudio", url)
            
        elif "gpt-for-all" in engine or "gpt4all" in engine:
            # GPT4All typically runs on port 4891 locally if using the API server
            url = config.get("gpt4all_url", "http://localhost:4891/v1")
            provider = OpenAICompatibleProvider("GPT4All", url)
            
        elif "vllm" in engine:
            url = config.get("vllm_url", "http://localhost:8000/v1")
            provider = OpenAICompatibleProvider("vLLM", url)
            
        else:
            # Fallback or placeholder for other engines
            # In Phase 2 we will add Gemini, Claude, etc.
            raise ValueError(f"Provider {engine_name} not yet integrated or supported in this phase.")

        cls._providers[provider_key] = provider
        return provider

provider_factory = ProviderFactory()
