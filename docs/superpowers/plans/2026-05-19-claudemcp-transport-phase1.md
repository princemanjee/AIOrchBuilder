# ClaudeMCP-as-Transport — Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace AIOrchBuilder's brittle per-provider HTTP layer with ClaudeMCP as a single transport gateway (via its faithful Anthropic `/v1/messages` endpoint), turn `llm_router` into the model-selection brain with fallback, and convert the build engines from emitting hand-written template stubs to producing real LLM-generated artifacts — proven end-to-end on the DATA agent.

**Architecture:** AIOrchBuilder talks to one endpoint — ClaudeMCP at `http://localhost:3210/v1/messages` — using a new `AnthropicGatewayProvider`. ClaudeMCP handles protocol translation, backend selection (Claude via Max-subscription CLI, Gemini, Ollama, LM Studio), caching, and the audit archive. AIOrchBuilder's `llm_router` decides *which* model name to send per agent/phase and supplies an ordered fallback list; a shared `llm_client.agent_generate()` helper injects the relevant `AGENT_CONTRACTS.md` contract + blueprint + upstream artifacts as context, calls the gateway, and retries down the fallback chain on failure. The build engines gain LLM-driven generators; `orchestrator.run_simulation` awaits them instead of sleeping.

**Tech Stack:** Python 3 / FastAPI / httpx (async) / pytest + pytest-asyncio + respx (HTTP mocking) on the AIOrchBuilder side; Node 20 / ClaudeMCP on the gateway side.

**Why the Anthropic endpoint, not OpenAI:** ClaudeMCP's OpenAI `/v1/chat/completions` shim (`src/openaiShim/promptBuilder.ts`) injects an agentic harness system prompt and STRICT format rules that forbid JSON wrappers and code fences, and it hard-rejects `response_format`. That corrupts both blueprint JSON parsing and code generation. The Anthropic `/v1/messages` shim (`src/anthropicShim/requestTranslator.ts` → `normalizeSystem`) passes the system prompt and messages through verbatim. Phase 1 therefore standardizes on `/v1/messages`.

**Scope boundary:** This plan delivers working software on its own: the gateway transport, the router rewrite, the generation helper, and the DATA agent producing real LLM-generated SQL through the full `parse → decompose → approve → download` pipeline. Converting the remaining engines (API/UI/AUTH/TEST/LOGIC) is mechanical repetition of Task 9's pattern and is captured as the final task.

---

## File Structure

- `C:\Code\GitHub\ClaudeMCP\configs\default.json` — **Create.** Gateway runtime config (apiKey, enabled backends, default backend).
- `backend/providers/anthropic_gateway.py` — **Create.** `AnthropicGatewayProvider`, a drop-in `LLMProvider` that POSTs `/v1/messages`.
- `backend/providers/factory.py` — **Rewrite.** Collapse five per-provider branches to a single cached gateway provider.
- `backend/llm_router.py` — **Modify.** Add `resolve_gateway_models(phase, agent, config)` returning an ordered list of ClaudeMCP model names (primary + fallbacks).
- `backend/agent_specs.py` — **Create.** Per-agent system prompts + which context to inject. Data-driven so each engine conversion is configuration, not bespoke code.
- `backend/llm_client.py` — **Create.** `agent_generate(...)` — builds the prompt from a spec + context, calls the provider, walks the fallback chain, returns text.
- `backend/data_engine.py` — **Modify.** Add `async generate_schema_llm(data_layer, project_name)` alongside the existing deterministic `generate_schema` (kept as offline fallback).
- `backend/orchestrator.py` — **Modify.** `run_simulation` awaits LLM generation for AGENT_DATA; remove the `random.uniform` sleep; on generation failure, fall back to the deterministic generator and mark the task.
- `backend/main.py` — **Modify.** Add `gateway_url`, `gateway_api_key`, `gateway_default_max_tokens` to `DEFAULT_CONFIG` and `AdminConfigRequest`.
- `backend/requirements.txt` — **Modify.** Add `pytest`, `pytest-asyncio`, `respx`.
- `backend/pytest.ini` — **Create.** Configure asyncio mode.
- `backend/tests/__init__.py`, `backend/tests/test_*.py` — **Create.** Unit tests.

---

## Task 1: Stand up ClaudeMCP and confirm the Anthropic endpoint

**Files:**
- Create: `C:\Code\GitHub\ClaudeMCP\configs\default.json`

- [ ] **Step 1: Create the gateway config from the annotated example**

Copy `configs/example.json` to `configs/default.json` and set a real shared key. Minimal working content:

```json
{
  "apiKey": "aiorch-local-dev-key-2026",
  "claude": { "enabled": true, "command": "claude", "priority": 100, "timeoutMs": 600000 },
  "gemini": { "enabled": false, "command": "gemini", "priority": 90, "timeoutMs": 600000 },
  "lmstudio": { "enabled": false, "instances": [] },
  "ollama": {
    "enabled": true,
    "useNativeApi": false,
    "instances": [
      { "name": "local", "baseUrl": "http://127.0.0.1:11434", "priority": 40, "timeoutMs": 300000, "useNativeApi": null }
    ]
  },
  "router": { "defaultBackend": "claude", "localProbeIntervalMs": 60000 },
  "files": { "dir": "data/files", "ttlMs": 604800000, "maxTotalBytes": 5368709120 },
  "cache": { "file": "data/response-cache.json", "ttlMs": 3600000, "maxEntries": 500 },
  "archive": { "dbPath": "data/archive.sqlite", "compressionLevel": 3 },
  "embeddings": { "legacyBackendUrl": "", "legacyApiKey": "", "legacyTimeoutMs": 30000 },
  "adminUi": { "enabled": true, "bindLocalhost": true, "sessionTtlMs": 3600000 }
}
```

- [ ] **Step 2: Start the gateway**

Run (in `C:\Code\GitHub\ClaudeMCP`): `npm install` then `npm run dev`
Expected: console prints `ClaudeMCP listening on http://127.0.0.1:3210`

- [ ] **Step 3: Confirm the Anthropic endpoint passes the system prompt through and returns text**

Run (PowerShell, from any dir):

```powershell
$body = @'
{"model":"claude-code-cli","max_tokens":64,"system":"Reply with exactly the word PONG and nothing else.","messages":[{"role":"user","content":"ping"}]}
'@
curl.exe -s -X POST http://127.0.0.1:3210/v1/messages -H "x-api-key: aiorch-local-dev-key-2026" -H "anthropic-version: 2023-06-01" -H "Content-Type: application/json" -d $body
```

Expected: JSON containing `"content":[{"type":"text","text":"PONG"...}]`. If you get `401`, the `x-api-key` does not match `configs/default.json`. If you get a non-PONG chatty reply, that confirms the system prompt is honored (no harness prelude) — which is the whole reason we use this endpoint.

- [ ] **Step 4: Commit (ClaudeMCP repo)**

```bash
cd /c/Code/GitHub/ClaudeMCP && git add configs/default.json && git commit -m "chore: add local default config for AIOrchBuilder transport"
```

---

## Task 2: Add the test harness to the AIOrchBuilder backend

**Files:**
- Modify: `backend/requirements.txt`
- Create: `backend/pytest.ini`
- Create: `backend/tests/__init__.py`

- [ ] **Step 1: Add test dependencies**

Append to `backend/requirements.txt`:

```
pytest
pytest-asyncio
respx
```

- [ ] **Step 2: Configure pytest asyncio mode**

Create `backend/pytest.ini`:

```ini
[pytest]
asyncio_mode = auto
testpaths = tests
```

- [ ] **Step 3: Create the test package marker**

Create `backend/tests/__init__.py` (empty file).

- [ ] **Step 4: Install and verify the runner works**

Run (in `backend/`): `pip install -r requirements.txt && python -m pytest -q`
Expected: `no tests ran` (exit 5) — the runner is wired up.

- [ ] **Step 5: Commit**

```bash
git add backend/requirements.txt backend/pytest.ini backend/tests/__init__.py
git commit -m "test: add pytest+respx harness to backend"
```

---

## Task 3: AnthropicGatewayProvider

**Files:**
- Create: `backend/providers/anthropic_gateway.py`
- Test: `backend/tests/test_anthropic_gateway.py`

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_anthropic_gateway.py`:

```python
import httpx
import respx
import pytest
from providers.anthropic_gateway import AnthropicGatewayProvider

GATEWAY = "http://localhost:3210"


@pytest.mark.asyncio
@respx.mock
async def test_generate_sends_anthropic_shape_and_parses_text():
    route = respx.post(f"{GATEWAY}/v1/messages").mock(
        return_value=httpx.Response(
            200,
            json={"content": [{"type": "text", "text": "SELECT 1;"}]},
        )
    )
    provider = AnthropicGatewayProvider(GATEWAY, "secret-key", default_max_tokens=512)

    out = await provider.generate(
        prompt="make a schema",
        system_prompt="you are AGENT_DATA",
        model="claude-sonnet-4-5",
    )

    assert out == "SELECT 1;"
    assert route.called
    assert route.calls.last.request.headers["x-api-key"] == "secret-key"
    import json as _json
    payload = _json.loads(route.calls.last.request.content)
    assert payload["model"] == "claude-sonnet-4-5"
    assert payload["system"] == "you are AGENT_DATA"
    assert payload["messages"] == [{"role": "user", "content": "make a schema"}]
    assert payload["max_tokens"] == 512
    assert "thinking" not in payload


@pytest.mark.asyncio
@respx.mock
async def test_generate_concatenates_multiple_text_blocks():
    respx.post(f"{GATEWAY}/v1/messages").mock(
        return_value=httpx.Response(
            200,
            json={"content": [
                {"type": "text", "text": "part1 "},
                {"type": "tool_use", "id": "x", "name": "n", "input": {}},
                {"type": "text", "text": "part2"},
            ]},
        )
    )
    provider = AnthropicGatewayProvider(GATEWAY, "secret-key")
    out = await provider.generate(prompt="p", model="claude-code-cli")
    assert out == "part1 part2"


@pytest.mark.asyncio
@respx.mock
async def test_generate_raises_on_http_error():
    respx.post(f"{GATEWAY}/v1/messages").mock(return_value=httpx.Response(401, json={"error": "bad key"}))
    provider = AnthropicGatewayProvider(GATEWAY, "wrong-key")
    with pytest.raises(httpx.HTTPStatusError):
        await provider.generate(prompt="p", model="claude-code-cli")
```

- [ ] **Step 2: Run test to verify it fails**

Run (in `backend/`): `python -m pytest tests/test_anthropic_gateway.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'providers.anthropic_gateway'`

- [ ] **Step 3: Write minimal implementation**

Create `backend/providers/anthropic_gateway.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run (in `backend/`): `python -m pytest tests/test_anthropic_gateway.py -q`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add backend/providers/anthropic_gateway.py backend/tests/test_anthropic_gateway.py
git commit -m "feat(providers): add AnthropicGatewayProvider for ClaudeMCP transport"
```

---

## Task 4: Collapse the provider factory to the gateway

**Files:**
- Modify: `backend/providers/factory.py`
- Test: `backend/tests/test_factory.py`

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_factory.py`:

```python
from providers.factory import provider_factory
from providers.anthropic_gateway import AnthropicGatewayProvider


def test_factory_returns_gateway_provider_for_any_engine():
    provider_factory._providers.clear()
    cfg = {"gateway_url": "http://localhost:3210", "gateway_api_key": "k", "gateway_default_max_tokens": 2048}
    p = provider_factory.get_provider("AGENT_DATA", cfg)
    assert isinstance(p, AnthropicGatewayProvider)
    assert p.base_url == "http://localhost:3210"
    assert p.api_key == "k"
    assert p.default_max_tokens == 2048


def test_factory_caches_single_instance():
    provider_factory._providers.clear()
    cfg = {"gateway_url": "http://localhost:3210", "gateway_api_key": "k"}
    a = provider_factory.get_provider("AGENT_DATA", cfg)
    b = provider_factory.get_provider("AGENT_UI", cfg)
    assert a is b  # one transport for everything


def test_factory_defaults_url_and_key_when_missing():
    provider_factory._providers.clear()
    p = provider_factory.get_provider("anything", {})
    assert p.base_url == "http://localhost:3210"
    assert p.api_key == ""
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_factory.py -q`
Expected: FAIL — current factory raises `ValueError` for `AGENT_DATA` / does not build a gateway.

- [ ] **Step 3: Write minimal implementation**

Replace the entire contents of `backend/providers/factory.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_factory.py -q`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add backend/providers/factory.py backend/tests/test_factory.py
git commit -m "refactor(providers): collapse factory to single ClaudeMCP gateway"
```

---

## Task 5: Add gateway config keys to the backend

**Files:**
- Modify: `backend/main.py:115-152` (DEFAULT_CONFIG)
- Modify: `backend/main.py:156-170` (AdminConfigRequest)

- [ ] **Step 1: Add config keys to DEFAULT_CONFIG**

In `backend/main.py`, inside the `DEFAULT_CONFIG` dict (after `"active_model": "llama3",` on line 121), add:

```python
    "gateway_url": "http://localhost:3210",
    "gateway_api_key": "aiorch-local-dev-key-2026",
    "gateway_default_max_tokens": 4096,
```

- [ ] **Step 2: Expose the keys in AdminConfigRequest**

In `backend/main.py`, inside `class AdminConfigRequest`, after `active_model: Optional[str] = None`, add:

```python
    gateway_url: Optional[str] = None
    gateway_api_key: Optional[str] = None
    gateway_default_max_tokens: Optional[int] = None
```

- [ ] **Step 3: Verify the app imports cleanly**

Run (in `backend/`): `python -c "import main; print(main.system_config['gateway_url'])"`
Expected: `http://localhost:3210`

- [ ] **Step 4: Commit**

```bash
git add backend/main.py
git commit -m "feat(config): add ClaudeMCP gateway settings to system_config"
```

---

## Task 6: Repurpose llm_router to emit gateway model names with fallback

**Files:**
- Modify: `backend/llm_router.py`
- Test: `backend/tests/test_llm_router.py`

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_llm_router.py`:

```python
from llm_router import llm_router, ModelType


def test_phase_mapping_unchanged():
    assert llm_router.get_model_type_for_phase("04_BUILD") == ModelType.CODE
    assert llm_router.get_model_type_for_phase("01_ANALYSIS") == ModelType.SMART


def test_resolve_gateway_models_returns_ordered_list_with_fallbacks():
    models = llm_router.resolve_gateway_models("04_BUILD", "AGENT_DATA", {})
    assert isinstance(models, list) and len(models) >= 2
    # primary is a code-capable model name ClaudeMCP understands
    assert models[0] == "claude-sonnet-4-5"
    # last resort is always a free local model
    assert models[-1].startswith("ollama:")


def test_config_can_override_primary_per_agent():
    cfg = {"gateway_model_overrides": {"AGENT_DATA": "gemini-1.5-pro"}}
    models = llm_router.resolve_gateway_models("04_BUILD", "AGENT_DATA", cfg)
    assert models[0] == "gemini-1.5-pro"


def test_smart_phase_routes_to_opus_class_model():
    models = llm_router.resolve_gateway_models("01_ANALYSIS", "AGENT_LOGIC", {})
    assert models[0] == "claude-opus-4-7"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_llm_router.py -q`
Expected: FAIL — `AttributeError: 'LLMRouter' object has no attribute 'resolve_gateway_models'`

- [ ] **Step 3: Write minimal implementation**

In `backend/llm_router.py`, leave `ModelType`, `routing_map`, and `get_model_type_for_phase` unchanged. Replace `resolve_actual_model` with a gateway-aware resolver and add the fallback table:

```python
    # ModelType -> ordered list of ClaudeMCP model names (best first, free last).
    GATEWAY_MODELS = {
        ModelType.SMART: ["claude-opus-4-7", "claude-sonnet-4-5", "ollama:local/llama3"],
        ModelType.BALANCED: ["claude-sonnet-4-5", "gemini-1.5-flash", "ollama:local/llama3"],
        ModelType.FAST: ["gemini-1.5-flash", "ollama:local/phi3"],
        ModelType.CODE: ["claude-sonnet-4-5", "ollama:local/codellama"],
    }

    def resolve_gateway_models(self, phase: str, agent_name: str, config: dict) -> list:
        """Return an ordered list of ClaudeMCP model names: the agent override (if
        any) first, then the phase-appropriate chain. The gateway resolves each
        name to a backend; the caller tries them in order until one succeeds."""
        model_type = self.get_model_type_for_phase(phase)
        chain = list(self.GATEWAY_MODELS.get(model_type, self.GATEWAY_MODELS[ModelType.BALANCED]))
        override = (config or {}).get("gateway_model_overrides", {}).get(agent_name)
        if override:
            chain = [override] + [m for m in chain if m != override]
        return chain
```

> Note: `claude-opus-4-7` / `claude-sonnet-4-5` are routed by ClaudeMCP's `modelRouter` to the Claude CLI backend (the `claude-` prefix). `gemini-1.5-flash` → Gemini. `ollama:local/<m>` → the named Ollama instance. Adjust the exact model strings to whatever your Claude/Gemini subscription exposes.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_llm_router.py -q`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add backend/llm_router.py backend/tests/test_llm_router.py
git commit -m "feat(router): resolve phase/agent to ordered ClaudeMCP model chain"
```

---

## Task 7: Per-agent generation specs

**Files:**
- Create: `backend/agent_specs.py`
- Test: `backend/tests/test_agent_specs.py`

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_agent_specs.py`:

```python
from agent_specs import AGENT_SPECS, get_spec


def test_every_build_agent_has_a_spec():
    for agent in ["AGENT_DATA", "AGENT_API", "AGENT_UI", "AGENT_AUTH", "AGENT_TEST", "AGENT_LOGIC"]:
        spec = get_spec(agent)
        assert spec["phase"]
        assert "AGENT" in spec["system_prompt"]
        assert isinstance(spec["context_keys"], list)


def test_data_spec_requests_sql_and_rls():
    spec = get_spec("AGENT_DATA")
    sp = spec["system_prompt"].lower()
    assert "sql" in sp and "rls" in sp


def test_unknown_agent_raises():
    import pytest
    with pytest.raises(KeyError):
        get_spec("AGENT_NOPE")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_agent_specs.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'agent_specs'`

- [ ] **Step 3: Write minimal implementation**

Create `backend/agent_specs.py`. The `system_prompt` text below encodes the hard rules from `AGENT_CONTRACTS.md` so the model honors the contracts:

```python
# File: backend/agent_specs.py
# Per-agent generation specs. system_prompt encodes the AGENT_CONTRACTS.md rules
# so the LLM produces contract-compliant artifacts. context_keys names the
# blueprint sections to inject into the user prompt.

AGENT_SPECS = {
    "AGENT_DATA": {
        "phase": "04_BUILD",
        "context_keys": ["project_name", "data_layer"],
        "system_prompt": (
            "You are AGENT_DATA for AIOrchBuilder. Produce production-grade "
            "PostgreSQL/Supabase SQL. HARD RULES: every table MUST include RBAC "
            "fields created_by (uuid, references auth.users) and role_required "
            "(text) from Day 1; enable RLS on every table; emit CREATE TABLE plus "
            "matching RLS policies. Output ONLY the SQL — no prose, no code fences."
        ),
    },
    "AGENT_API": {
        "phase": "04_BUILD",
        "context_keys": ["project_name", "api_layer", "data_layer"],
        "system_prompt": (
            "You are AGENT_API for AIOrchBuilder. Produce FastAPI endpoint code "
            "that performs REAL Supabase CRUD against the given schema. HARD RULES: "
            "every endpoint requires an auth dependency; validate inputs with "
            "Pydantic; no placeholder 'return []' stubs. Output ONLY Python — no prose."
        ),
    },
    "AGENT_UI": {
        "phase": "04_BUILD",
        "context_keys": ["project_name", "ui_layer"],
        "system_prompt": (
            "You are AGENT_UI for AIOrchBuilder. Produce React/Next.js components "
            "using the provided style_guide tokens. HARD RULES: wire components to "
            "data via fetch/hooks (no alert() placeholders); glassmorphic aesthetic; "
            "no off-the-shelf component libraries. Output ONLY the component code — no prose."
        ),
    },
    "AGENT_AUTH": {
        "phase": "04_BUILD",
        "context_keys": ["project_name", "data_layer"],
        "system_prompt": (
            "You are AGENT_AUTH for AIOrchBuilder. Produce REAL Supabase JWT "
            "verification middleware and per-table RLS policies. HARD RULES: verify "
            "the bearer token against Supabase (no hardcoded user ids); least-privilege "
            "defaults. Output ONLY code — no prose."
        ),
    },
    "AGENT_TEST": {
        "phase": "05_VALIDATION",
        "context_keys": ["project_name", "api_layer", "data_layer"],
        "system_prompt": (
            "You are AGENT_TEST for AIOrchBuilder. Produce pytest unit tests and "
            "Playwright e2e tests that exercise the generated endpoints, including "
            "the 401-without-auth case. Output ONLY test code — no prose."
        ),
    },
    "AGENT_LOGIC": {
        "phase": "06_REFINEMENT",
        "context_keys": ["project_name", "description", "data_layer", "api_layer"],
        "system_prompt": (
            "You are AGENT_LOGIC for AIOrchBuilder. Produce service-layer business "
            "logic and integration functions that connect the API and data layers. "
            "HARD RULES: real implementations, not print() placeholders. Output ONLY code — no prose."
        ),
    },
}


def get_spec(agent_name: str) -> dict:
    return AGENT_SPECS[agent_name]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_agent_specs.py -q`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add backend/agent_specs.py backend/tests/test_agent_specs.py
git commit -m "feat(agents): add contract-encoded per-agent generation specs"
```

---

## Task 8: agent_generate() — the shared generation helper with fallback

**Files:**
- Create: `backend/llm_client.py`
- Test: `backend/tests/test_llm_client.py`

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_llm_client.py`:

```python
import pytest
from llm_client import agent_generate


class _StubProvider:
    def __init__(self, behavior):
        self.behavior = behavior  # dict model -> "text" | Exception
        self.calls = []

    def name(self):
        return "stub"

    async def generate(self, prompt, system_prompt="", model=None, **kwargs):
        self.calls.append(model)
        result = self.behavior[model]
        if isinstance(result, Exception):
            raise result
        return result


@pytest.mark.asyncio
async def test_uses_first_model_when_it_succeeds():
    provider = _StubProvider({"m1": "OK"})
    text = await agent_generate(
        provider, models=["m1", "m2"], system_prompt="sys",
        context={"project_name": "demo"}, instruction="go",
    )
    assert text == "OK"
    assert provider.calls == ["m1"]


@pytest.mark.asyncio
async def test_falls_back_to_next_model_on_failure():
    provider = _StubProvider({"m1": RuntimeError("down"), "m2": "OK2"})
    text = await agent_generate(
        provider, models=["m1", "m2"], system_prompt="sys",
        context={"project_name": "demo"}, instruction="go",
    )
    assert text == "OK2"
    assert provider.calls == ["m1", "m2"]


@pytest.mark.asyncio
async def test_raises_when_all_models_fail():
    provider = _StubProvider({"m1": RuntimeError("a"), "m2": RuntimeError("b")})
    with pytest.raises(RuntimeError):
        await agent_generate(
            provider, models=["m1", "m2"], system_prompt="sys",
            context={}, instruction="go",
        )


@pytest.mark.asyncio
async def test_context_is_serialized_into_the_prompt():
    captured = {}

    class _Capture(_StubProvider):
        async def generate(self, prompt, system_prompt="", model=None, **kwargs):
            captured["prompt"] = prompt
            return "OK"

    provider = _Capture({"m1": "OK"})
    await agent_generate(
        provider, models=["m1"], system_prompt="sys",
        context={"project_name": "demo", "data_layer": {"tables": []}},
        instruction="Generate the schema.",
    )
    assert "demo" in captured["prompt"]
    assert "Generate the schema." in captured["prompt"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_llm_client.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'llm_client'`

- [ ] **Step 3: Write minimal implementation**

Create `backend/llm_client.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_llm_client.py -q`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add backend/llm_client.py backend/tests/test_llm_client.py
git commit -m "feat(llm): add agent_generate helper with model fallback chain"
```

---

## Task 9: Convert AGENT_DATA to real LLM generation (reference pattern)

**Files:**
- Modify: `backend/data_engine.py`
- Test: `backend/tests/test_data_engine_llm.py`

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_data_engine_llm.py`:

```python
import pytest
from models import DataLayerSpec
from data_engine import agent_data


class _StubProvider:
    async def generate(self, prompt, system_prompt="", model=None, **kwargs):
        # Echo proof that context reached the model + return plausible SQL.
        assert "tasks" in prompt  # table name from the spec made it in
        return "CREATE TABLE public.tasks (id uuid primary key);"

    def name(self):
        return "stub"


@pytest.mark.asyncio
async def test_generate_schema_llm_calls_model_with_context():
    data_layer = DataLayerSpec(
        tables=[{"name": "tasks", "columns": [{"name": "title", "type": "text"}]}],
        rls_policies=["Users see own tasks"],
    )
    sql = await agent_data.generate_schema_llm(
        data_layer, project_name="demo", provider=_StubProvider(), models=["m1"]
    )
    assert "CREATE TABLE" in sql
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_data_engine_llm.py -q`
Expected: FAIL — `AttributeError: 'DataEngine' object has no attribute 'generate_schema_llm'` (or similar; the deterministic `generate_schema` exists, the LLM variant does not).

- [ ] **Step 3: Write minimal implementation**

In `backend/data_engine.py`, keep the existing deterministic `generate_schema`/`generate_seed_data` (they become the offline fallback). Add this async method to the engine class (use the actual class/instance name found in the file — the module exposes `agent_data`):

```python
    async def generate_schema_llm(self, data_layer, project_name: str, provider, models) -> str:
        """LLM-driven schema generation. Injects the blueprint data_layer and the
        AGENT_DATA contract; returns raw SQL. Caller supplies provider + model chain."""
        from agent_specs import get_spec
        from llm_client import agent_generate

        spec = get_spec("AGENT_DATA")
        context = {
            "project_name": project_name,
            "data_layer": data_layer.dict() if hasattr(data_layer, "dict") else data_layer,
        }
        instruction = (
            "Generate the complete PostgreSQL/Supabase schema (CREATE TABLE + RLS "
            "policies) for every table above. Honor the HARD RULES in your system prompt."
        )
        return await agent_generate(
            provider,
            models=models,
            system_prompt=spec["system_prompt"],
            context=context,
            instruction=instruction,
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_data_engine_llm.py -q`
Expected: PASS (1 passed)

- [ ] **Step 5: Commit**

```bash
git add backend/data_engine.py backend/tests/test_data_engine_llm.py
git commit -m "feat(data-engine): add LLM-driven schema generation via gateway"
```

---

## Task 10: Wire run_simulation to await real generation (with deterministic fallback)

**Files:**
- Modify: `backend/orchestrator.py:84-124` (the `run_simulation` loop + AGENT_DATA branch)
- Test: `backend/tests/test_orchestrator_data.py`

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_orchestrator_data.py`:

```python
import pytest
from models import ArchitectureBlueprint, DataLayerSpec, APILayerSpec, UILayerSpec, AgentTask
from orchestrator import task_orchestrator


def _blueprint():
    return ArchitectureBlueprint(
        project_name="demo",
        description="d",
        data_layer=DataLayerSpec(tables=[{"name": "tasks", "columns": []}], rls_policies=[]),
        api_layer=APILayerSpec(endpoints=[], middleware=[]),
        ui_layer=UILayerSpec(pages=[], components=[], style_guide={}),
        reasoning="r",
    )


@pytest.mark.asyncio
async def test_data_agent_uses_llm_output_when_generation_succeeds(monkeypatch):
    async def fake_llm(self, data_layer, project_name, provider, models):
        return "-- LLM SQL\nCREATE TABLE tasks();"

    monkeypatch.setattr("data_engine.agent_data.generate_schema_llm", fake_llm.__get__(__import__("data_engine").agent_data))

    task_orchestrator.current_blueprint = _blueprint()
    task = AgentTask(id="t1", agent_name="AGENT_DATA", task_description="d")
    seen = []

    async def cb(t):
        seen.append(t.status)

    await task_orchestrator.run_simulation([task], {"gateway_url": "http://x", "gateway_api_key": "k"}, cb)

    assert task.status == "complete"
    assert "LLM SQL" in task.artifacts["supabase/migrations/01_init.sql"]
    assert seen == ["in_progress", "complete"]


@pytest.mark.asyncio
async def test_data_agent_falls_back_to_deterministic_on_llm_failure(monkeypatch):
    async def boom(self, data_layer, project_name, provider, models):
        raise RuntimeError("gateway down")

    monkeypatch.setattr("data_engine.agent_data.generate_schema_llm", boom.__get__(__import__("data_engine").agent_data))

    task_orchestrator.current_blueprint = _blueprint()
    task = AgentTask(id="t1", agent_name="AGENT_DATA", task_description="d")

    async def cb(t):
        pass

    await task_orchestrator.run_simulation([task], {"gateway_url": "http://x", "gateway_api_key": "k"}, cb)

    # Deterministic generator still produces valid SQL; build does not crash.
    assert task.status == "complete"
    assert "CREATE TABLE" in task.artifacts["supabase/migrations/01_init.sql"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_orchestrator_data.py -q`
Expected: FAIL — current `run_simulation` calls the synchronous `agent_data.generate_schema(...)` and never invokes `generate_schema_llm`; the first test's assertion on `"LLM SQL"` fails.

- [ ] **Step 3: Write minimal implementation**

In `backend/orchestrator.py`:

(a) Add imports near the top (after the existing `from llm_router import ...`):

```python
from llm_client import agent_generate  # noqa: F401  (used by engines)
```

(b) Remove the simulation sleep on line 114 (`await asyncio.sleep(random.uniform(1.0, 2.0))`). Delete that line.

(c) Replace the AGENT_DATA block (current lines 117-124) with an LLM-first, deterministic-fallback version. Inside the `for task in tasks:` loop, after `task.status = "in_progress"` / `await callback(task)`:

```python
            if task.agent_name == "AGENT_DATA" and self.current_blueprint:
                models = llm_router.resolve_gateway_models("04_BUILD", "AGENT_DATA", config)
                try:
                    sql = await agent_data.generate_schema_llm(
                        self.current_blueprint.data_layer,
                        self.current_blueprint.project_name,
                        provider,
                        models,
                    )
                    print(f"📁 LLM-generated SQL for {task.agent_name}")
                except Exception as e:
                    print(f"⚠️ LLM schema generation failed ({e}); using deterministic fallback.")
                    sql = agent_data.generate_schema(self.current_blueprint.data_layer)
                task.artifacts = {
                    "supabase/migrations/01_init.sql": sql,
                    "supabase/seed.sql": agent_data.generate_seed_data(self.current_blueprint.data_layer),
                }
                task.output_artifact = sql
```

> `provider` is already created earlier in the loop (line 106, `provider = provider_factory.get_provider(engine, config)`). Ensure that assignment is not inside the `try/except` that only logs — move it out so `provider` is always bound, or pass `provider_factory.get_provider(engine, config)` directly.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_orchestrator_data.py -q`
Expected: PASS (2 passed)

- [ ] **Step 5: Run the full suite**

Run (in `backend/`): `python -m pytest -q`
Expected: PASS (all tests from Tasks 3–10)

- [ ] **Step 6: Commit**

```bash
git add backend/orchestrator.py backend/tests/test_orchestrator_data.py
git commit -m "feat(orchestrator): AGENT_DATA generates real SQL via gateway with fallback"
```

---

## Task 11: End-to-end verification through the live gateway

**Files:** none (manual verification)

- [ ] **Step 1: Ensure ClaudeMCP is running** (Task 1) and `claude` CLI is authenticated.

- [ ] **Step 2: Start the backend**

Run (in `backend/`): `uvicorn main:app --reload --port 8001`

- [ ] **Step 3: Drive the pipeline with the sample payload**

Run (PowerShell, repo root):

```powershell
$idea = Get-Content -Raw no9-idea.json
$bp = curl.exe -s -X POST http://localhost:8001/logic/parse-requirements -H "Content-Type: application/json" -d (@{prompt=$idea} | ConvertTo-Json)
$bp | Out-File -Encoding utf8 _bp.json
curl.exe -s -X POST http://localhost:8001/logic/decompose -H "Content-Type: application/json" -d (Get-Content -Raw _bp.json)
```

Expected: `parse-requirements` returns a real `ArchitectureBlueprint` JSON produced by Claude (not the mocked fallback); `decompose` returns six tasks.

- [ ] **Step 4: Approve and inspect the DATA artifact**

Approve the build (POST `/logic/approve-build` with the approval body), then `GET /logic/download-bundle`, unzip, and open `supabase/migrations/01_init.sql`.
Expected: SQL with `created_by`, `role_required`, and `ENABLE ROW LEVEL SECURITY` on each table — generated by the model, not the template. Compare against `portfolio_output/` to confirm it is materially richer than the old stub output.

- [ ] **Step 5: Commit any config tweaks discovered during verification**

```bash
git add -A && git commit -m "chore: tune gateway model names after e2e verification"
```

---

## Task 12: Convert the remaining engines (API, UI, AUTH, TEST, LOGIC)

This repeats Task 9 + Task 10 exactly, once per agent, using the spec already defined in `agent_specs.py` (Task 7). For each agent below, (1) add an `async generate_*_llm(...)` method to its engine module that calls `agent_generate(provider, models, spec["system_prompt"], context, instruction)`, (2) replace that agent's branch in `run_simulation` with the LLM-first / deterministic-fallback pattern from Task 10 Step 3(c), and (3) add a matching test mirroring `test_orchestrator_data.py`.

- [ ] **AGENT_API** — engine `backend/api_engine.py`; phase `04_BUILD`; context `{project_name, api_layer, data_layer}`; instruction: "Generate FastAPI routers + Pydantic models with real Supabase CRUD for every endpoint above." Fallback: existing `agent_api.generate_router/generate_models/...`.
- [ ] **AGENT_UI** — engine `backend/ui_engine.py`; phase `04_BUILD`; context `{project_name, ui_layer}`; instruction: "Generate each page and component using the style_guide tokens; wire to data, no alert() placeholders." Fallback: existing `agent_ui.generate_page/generate_component/...` (loop per page/component as in `orchestrator.py:137-153`).
- [ ] **AGENT_AUTH** — engine `backend/auth_engine.py`; phase `04_BUILD`; context `{project_name, data_layer}`; instruction: "Generate real Supabase JWT middleware and per-table RLS policies." Fallback: existing `agent_auth.generate_auth_middleware/generate_rls_sql/...`.
- [ ] **AGENT_TEST** — engine `backend/test_engine.py`; phase `05_VALIDATION`; context `{project_name, api_layer, data_layer}`; instruction: "Generate pytest unit tests and Playwright e2e tests, including the 401-without-auth case." Fallback: existing `agent_test.*`.
- [ ] **AGENT_LOGIC** — engine `backend/logic_engine.py` (the `generate_*_logic` methods); phase `06_REFINEMENT`; context `{project_name, description, data_layer, api_layer}`; instruction: "Generate real service-layer logic and integration functions (no print() placeholders)." Fallback: existing `agent_logic.generate_frontend_logic/generate_backend_logic`.

- [ ] **Final step: full suite + e2e**

Run: `python -m pytest -q` (all green), then repeat Task 11 and confirm every layer's artifacts are LLM-generated with deterministic fallback intact.

```bash
git add -A && git commit -m "feat(engines): LLM-driven generation for API/UI/AUTH/TEST/LOGIC agents"
```

---

## Self-Review Notes

- **Spec coverage:** transport (Tasks 1,3,5) · single endpoint via Anthropic shim (Task 3) · router-as-brain with fallback (Task 6) · contracts-as-context (Tasks 7,8) · real generation proven on DATA end-to-end (Tasks 9–11) · remaining engines (Task 12). The `parse-requirements` path needs no code change — once the factory returns the gateway (Task 4) and config carries `gateway_*` (Task 5), `logic_engine.parse()` flows through ClaudeMCP unchanged; Task 11 Step 3 verifies it.
- **Out of scope (later phases):** execution sandbox / live preview / iteration loop (Phase 2); Supabase-backed multi-user state replacing the `"current_session"` dicts (Phase 3); in-browser editor + deploy (Phase 4). The hardcoded `POSTGRES_PASSWORD=secret` and faked health check are tracked for Phase 2 hardening.
- **Type consistency:** `agent_generate(provider, models, system_prompt, context, instruction, **gen_kwargs)` and `resolve_gateway_models(phase, agent_name, config)` signatures are used identically in Tasks 8, 9, 10, 12. Provider contract is the existing `LLMProvider.generate(prompt, system_prompt, model, **kwargs) -> str`.
