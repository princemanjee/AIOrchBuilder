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
