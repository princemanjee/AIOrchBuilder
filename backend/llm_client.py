# File: backend/llm_client.py
import json
from typing import Any, Dict, List


def _serialize_context(context: Dict[str, Any]) -> str:
    parts = []
    for key, value in context.items():
        if isinstance(value, (dict, list)):
            rendered = json.dumps(value, indent=2, default=str)
        else:
            rendered = str(value)
        parts.append(f"## {key}\n{rendered}")
    return "\n\n".join(parts)


async def agent_generate(
    provider,
    models: List[str],
    system_prompt: str,
    context: Dict[str, Any],
    instruction: str,
    **gen_kwargs,
) -> str:
    """Build a prompt from context + instruction, call the provider, and walk the
    `models` fallback chain until one succeeds. Re-raises the last error if all fail."""
    prompt = (
        f"{_serialize_context(context)}\n\n"
        f"# TASK\n{instruction}"
    ).strip()

    last_error: Exception | None = None
    for model in models:
        try:
            return await provider.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                model=model,
                **gen_kwargs,
            )
        except Exception as e:  # noqa: BLE001 — intentional: try next model
            last_error = e
            print(f"⚠️ Model '{model}' failed ({e}); trying next in chain...")

    assert last_error is not None
    raise last_error
