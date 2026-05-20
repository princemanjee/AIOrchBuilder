# File: backend/providers/anthropic_gateway.py
import httpx
from typing import Optional
from .base import LLMProvider

# Sampling/forwardable params the ClaudeMCP Anthropic shim accepts.
# NOTE: 'thinking' is deliberately excluded — the shim rejects it (Plan 04).
_FORWARD_KEYS = ("temperature", "top_p", "top_k", "stop_sequences")


class AnthropicGatewayProvider(LLMProvider):
    """Talks to ClaudeMCP's faithful Anthropic Messages endpoint (/v1/messages).

    Unlike the OpenAI shim, this path passes the system prompt through verbatim,
    so JSON and fenced code survive intact.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        default_max_tokens: int = 4096,
        timeout: float = 600.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.default_max_tokens = default_max_tokens
        self.timeout = timeout

    def name(self) -> str:
        return "ClaudeMCP-Gateway"

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        model: Optional[str] = None,
        **kwargs,
    ) -> str:
        url = f"{self.base_url}/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model or "claude-code-cli",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": int(kwargs.get("max_tokens", self.default_max_tokens)),
        }
        if system_prompt:
            payload["system"] = system_prompt
        for k in _FORWARD_KEYS:
            if k in kwargs and kwargs[k] is not None:
                payload[k] = kwargs[k]

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        return "".join(
            block.get("text", "")
            for block in data.get("content", [])
            if block.get("type") == "text"
        )
