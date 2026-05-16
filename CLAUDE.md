# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Frontend (Next.js, root directory)
- `npm run dev` — start Next.js dev server on port 3000
- `npm run build` — production build (Dockerfile expects this to succeed)
- `npm run start` — run the built app
- `npm run lint` — `next lint`

There is no test runner wired up in `package.json`.

### Backend (FastAPI, `backend/`)
- `cd backend && pip install -r requirements.txt`
- `cd backend && uvicorn main:app --reload --port 8001` — dev server
- `cd backend && python integration_test.py` — end-to-end orchestrator smoke test. Reads `no9-idea.json` from the repo root as a sample input and falls back to a mocked blueprint if no LLM provider is reachable. This is the closest thing to a test suite.

### Full stack
- `docker-compose up` — boots frontend (port 3000) and orchestrator (port 8001) together. See `DEPLOY_GUIDE.md` for the production variant.

### Environment
Copy `.env.example` to `.env`. Both the Next.js app (`NEXT_PUBLIC_SUPABASE_*`) and the FastAPI backend (`SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`) read from it.

## Architecture

This repo is **two applications plus a doctrine layer**. Understanding all three is required before making structural changes.

### 1. Frontend: Next.js 14 App Router dashboard (`src/`)
- `src/app/page.tsx` is a single large client component implementing the entire admin dashboard (tabs, agent config, blueprint review, build approval, artifact viewer). State is local — there is no global store.
- `src/components/ui/Glass*.tsx` are the design primitives. The visual language is "glassmorphic"; do not introduce default browser styles or off-the-shelf component libraries (per `AGENT_CONTRACTS.md` → AGENT_UI rule).
- `src/lib/supabase.ts` exports `hubClient` plus a `getSatelliteClient(projectId, url?, key?)` factory. This mirrors the Hub/Satellite split on the backend (see below) — the frontend can talk to multiple Supabase projects at once.
- TS path alias: `@/*` → `src/*`.

### 2. Backend: FastAPI orchestrator (`backend/`)
The backend is the actual orchestration engine. `main.py` wires everything; the rest are the moving parts.

**Hub/Satellite Supabase model** (`main.py` → `ClientRegistry`):
- The **Hub** is the central Supabase project — holds `projects`, `tasks`, `agent_audit_logs` (schema in `database/schema.sql`).
- **Satellites** are per-project Supabase instances registered via `POST /connect-satellite`. On startup, the Hub's `projects` table is queried and satellite clients are recreated from stored `satellite_url` / `satellite_key`. All audit logs go to the Hub; per-project data goes to the matching satellite. When adding endpoints, route to `registry.hub` for global telemetry and `registry.get_satellite(project_id)` for project-scoped data.

**Build pipeline** (`POST /logic/parse-requirements` → `POST /logic/decompose` → `POST /logic/approve-build` → `GET /logic/download-bundle`):
1. `agent_logic.parse()` (in `logic_engine.py`) turns a free-text prompt into an `ArchitectureBlueprint` via the active LLM provider.
2. `task_orchestrator.decompose()` (in `orchestrator.py`) walks the blueprint and emits an ordered `List[AgentTask]` with explicit dependency edges: DATA → API → UI → AUTH → TEST → LOGIC (integration). The dependency graph here is the source of truth for build order — change it carefully.
3. Approval triggers `task_orchestrator.run_simulation()` as an asyncio background task. Per task, it (a) consults `system_config["agent_mappings"]` to pick an engine, (b) asks `llm_router` for a `ModelType` based on phase, (c) calls the per-agent engine module (`data_engine`, `api_engine`, `ui_engine`, `auth_engine`, `test_engine`, `logic_engine`, `doc_engine`) to produce **real file artifacts** stored on `task.artifacts: Dict[path, content]`, and (d) fires a callback that writes to `agent_audit_logs` on the Hub.
4. `/logic/download-bundle` zips every task's `artifacts` map into a downloadable project skeleton.

**LLM provider plumbing**:
- `llm_router.py` maps SDLC phases (`01_ANALYSIS` … `06_REFINEMENT`) to a `ModelType` (SMART/BALANCED/FAST/CODE), then resolves that to a concrete model string per engine.
- `providers/factory.py` returns `OpenAICompatibleProvider` instances for Ollama, LM Studio, GPT4All, vLLM, and Perplexity. All are treated as OpenAI-compatible HTTP endpoints. Adding a non-compatible provider (Anthropic native, Gemini native) means adding a new `LLMProvider` subclass under `providers/`, not extending the OpenAI one.
- `system_config` in `main.py` is the live mutable config — it's the same object exposed via `GET/POST /admin/config`. Admin-mutated fields (engine URLs, agent→engine mappings, revision limit) propagate by reference into `run_simulation`.

**Approval / history caveats**:
- `pending_approvals` and `project_history` are in-memory dicts keyed by the literal string `"current_session"`. This means the backend is **single-session by design** at the POC stage — do not assume multi-tenant isolation. Anything multi-user requires replacing these dicts with Supabase-backed state.

### 3. Doctrine layer (`AppBuilder.md`, `AGENT_CONTRACTS.md`, `.agent/rules/`, `.agent/workflows/`, `ContextFile.xml`, `GEMINI.MD`)
These are **not** documentation of the code — they are the prompt/system-instruction corpus the orchestrator injects into an LLM to make it behave as the orchestrator persona. `AppBuilder.md` is the monolithic SOP; `.agent/rules/` and `.agent/workflows/` are the same content split per concern. `AGENT_CONTRACTS.md` defines each agent's contract and hard rules (e.g., "AGENT_DATA must implement RBAC fields on every table from Day 1"; "AGENT_API endpoints must require auth headers"). When generating code via an agent module in `backend/*_engine.py`, those contracts are the spec — honor them when extending the engines.

## Conventions worth knowing
- Both the frontend dashboard and the backend orchestrator default to assuming the user has the `admin` role. The backend gates admin endpoints on an `X-Role: admin` header (`/admin/config`, `/admin/reset`) — not a real auth check, just a placeholder.
- The Notion scripts at the repo root (`create_notion_dashboard*.py`, `update_notion_probe.py`) are personal tooling, are gitignored, and are not part of the application.
- `no9-idea.json` is a sample resume payload used by `backend/integration_test.py` — keep it around if you touch the integration test.
