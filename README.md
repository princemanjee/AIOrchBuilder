# AIOrchBuilder

A multi-agent orchestration framework that builds applications by decomposing them into specialist agent tasks, routing each task to the optimal large language model, and assembling the results into deployable software.

This is the meta-framework. It generates the structured prompts, the agent contracts, and the orchestration logic. Real applications built on top of it (for example, the FieldForce Tool Tracker referenced below) prove that the methodology works on production-scale problems.

## Why this exists

Modern application development with large language models is constrained in two ways at once. Single-model approaches force one general-purpose model to handle architecture, UI, business logic, data, security, and testing equally well, which no model does. Naive multi-model approaches lose context and consistency at the boundaries between calls.

AIOrchBuilder addresses both constraints. Each phase of an application build is assigned to a specialist agent with a defined contract, and the orchestrator routes each agent's tasks to the model best suited for that kind of work. Architectural reasoning goes to high-context reasoning models. Routine boilerplate goes to fast, cheap models. Data schema design goes to models with strong structured-output capability. The result is faster builds, lower per-build cost, and more consistent output across the parts of an application that have historically been hardest to keep coherent.

## The agent roster

The framework defines seven specialist agents, each with its own input contract, output contract, and rule set. The full specifications live in [AGENT_CONTRACTS.md](AGENT_CONTRACTS.md).

| Agent | Focus | Output |
| --- | --- | --- |
| AGENT_UI | Premium aesthetics, responsive design | HTML, Vanilla CSS, React components with custom design tokens |
| AGENT_LOGIC | Business logic, state, algorithms | Modular, testable JavaScript or Python functions |
| AGENT_DATA | Schemas and persistence | SQL or Prisma schemas, migration scripts, RBAC fields from Day 1 |
| AGENT_API | Endpoints and connectivity | REST or GraphQL endpoints with OpenAPI documentation |
| AGENT_AUTH | Identity and security | JWT sessions, role validation middleware, least-privilege defaults |
| AGENT_TEST | Quality assurance | Unit and end-to-end test suites with pass/fail reports |
| AGENT_REVIEW | Governance and compliance | Pull request feedback on performance, security, and readability |

The orchestrator coordinates handoffs between agents, enforces the contracts, and logs every action to an auditable Retrospective Audit Path.

## Dynamic LLM routing

The orchestrator does not pick one model for the whole build. It evaluates task complexity per agent invocation and routes to the model that matches.

- High complexity (architecture, multi-step reasoning) routes to Claude 3.5 Sonnet or GPT-4o.
- UI and aesthetic work routes to Claude 3.5 Sonnet or Gemini 1.5 Pro.
- Routine code and boilerplate routes to Gemini 1.5 Flash.
- Data and schema validation routes to GPT-4o-mini.

The provider abstraction layer (in `backend/providers/`) implements a factory pattern over an OpenAI-compatible interface. Adding a new provider is a matter of writing one adapter class. This includes **Ollama support for self-hosted local models**, which means the entire orchestration framework can run against locally hosted Llama, Mistral, or other open-weight models. That matters for cost control at scale and for any deployment where data residency or privacy rules out commercial API providers.

## Security model

Security is wired in from Day 1, not bolted on. Every operation is associated with a `user_id` and a role (Admin, Developer, or Auditor). Every database table includes RBAC fields (`created_by`, `role_required`). Every API endpoint requires authentication. Every agent action is logged to the audit trail. The Supabase row-level security (RLS) policies enforce access control at the database layer, so a compromise of the application layer does not automatically expose the data.

## Tech stack

**Frontend:** Next.js with TypeScript, React, lucide-react for iconography, Supabase client SDK for authentication and data, custom Glassmorphism design system (GlassButton, GlassCard, GlassInput components).

**Backend:** Python with FastAPI-style modular engines per agent role, dedicated `llm_router.py` for dynamic model selection, `orchestrator.py` for cross-agent coordination, provider abstraction layer supporting OpenAI-compatible APIs and Ollama.

**Data and Auth:** Supabase (PostgreSQL with Row-Level Security, JWT auth, real-time subscriptions).

**Deployment:** Docker Compose stack with frontend on port 3000, backend on port 8001, Nginx reverse proxy for SSL termination.

**Observability:** Notion-backed Retrospective Audit Path for every agent action (see `create_notion_dashboard.py` for the dashboard schema).

## Status

This is an active prototype, not a one-command demo. It has been used to scaffold real applications and the architecture has been validated on production-grade workloads. Deployment requires a Supabase project, an LLM provider configuration (cloud or Ollama), and approximately the resources outlined in the deployment guide. See [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md) for the full setup walkthrough.

If you want to run it locally for evaluation, the short version is: clone the repo, configure a Supabase project with the schema in `database/`, set the environment variables in `.env`, and run `docker-compose up`. The full version, including reverse proxy, SSL, and security hardening, is in DEPLOY_GUIDE.md.

## Project structure

```
.
├── AGENT_CONTRACTS.md          # Full specifications for each agent role
├── AppBuilder.md               # Application build workflow documentation
├── CLAUDE.md                   # Project-specific guidance for AI assistants
├── DEPLOY_GUIDE.md             # Production deployment walkthrough
├── backend/                    # Python orchestration backend
│   ├── orchestrator.py         # Cross-agent coordination
│   ├── llm_router.py           # Dynamic model selection
│   ├── *_engine.py             # Seven specialist agent engines
│   ├── providers/              # LLM provider abstraction (factory pattern)
│   ├── models.py               # Data models
│   ├── integration_test.py     # Integration tests
│   └── Dockerfile
├── src/                        # Next.js frontend
│   ├── app/                    # Pages and layouts
│   ├── components/             # Dashboard and Glassmorphism UI components
│   └── lib/                    # Supabase client and shared utilities
├── database/                   # Schema, migrations, RBAC policies
├── docker-compose.yml
└── README.md
```

## Related work

This framework was the foundation for the **FieldForce Tool Tracker**, a real-time GPS asset management platform for utility and large-scale construction operations. FieldForce demonstrates the methodology end-to-end: a monorepo with three apps (NestJS API, React 18 dashboard, React Native mobile), enterprise-grade auth via Keycloak, time-series tracking with PostgreSQL + PostGIS + TimescaleDB, messaging via NATS JetStream, and offline support on mobile. The AIOrchBuilder agent contracts and orchestration patterns informed how the FieldForce codebase is structured. Case study coming to princerehman.com/work/fieldforce.

The conceptual lineage runs through three projects on this account:

1. **[EngineeredPromptLibrary](https://github.com/princemanjee/EngineeredPromptLibrary)** is the prompt and context engineering foundation, including the Reasoning Strategies for AI Decision Making paper that informed the orchestrator design.
2. **AIOrchBuilder** (this repo) is the multi-agent meta-framework that grew out of that foundation.
3. **FieldForce Tool Tracker** is the production application built using the meta-framework.

## Author

Built by **P. R. Manjee**. Digital transformation consultant focused on AI adoption, cloud modernization, and the operational realities of moving from prototype to production. MIT Sloan (MS Digital Transformation), MIT (MS Information Systems), Notre Dame (BS Electrical Engineering). [princerehman.com](https://princerehman.com).

## License

See [LICENSE](LICENSE).
