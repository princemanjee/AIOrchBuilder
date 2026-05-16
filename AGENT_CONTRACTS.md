# 🤖 AGENT_CONTRACTS: Specialist Definitions & Protocols

This document defines the specialized behaviors, instruction sets, and communication contracts for the AIOrchBuilder swarm.

---

## 🛰️ Orchestrator Governance

### 🧠 Dynamic LLM Routing Logic
The Orchestrator evaluates task complexity and routes to the optimal model:
- **High Complexity (Architectural/Logic)**: `Claude 3.5 Sonnet` or `GPT-4o`.
- **UI/UX Aesthetics**: `Claude 3.5 Sonnet` or `Gemini 1.5 Pro`.
- **Routine Code/Boilerplate**: `Gemini 1.5 Flash`.
- **Data/Schema Validation**: `GPT-4o-mini`.

### 🛡️ Security Protocol (Day 1)
- **Role-Based Access Control (RBAC)**: All operations must be associated with a `user_id` and `role` (Admin, Developer, Auditor).
- **Audit Logging**: Every agent action must be logged to the `Retrospective Audit Path` in Notion.

---

## 🎨 AGENT_UI
**Focus**: Premium Aesthetics & Responsive Design.
- **Contract**: Accepts wireframes/journeys; Outputs HTML/Vanilla CSS/React components.
- **Rule**: Never use default browser styles; always implement custom design tokens.

## ⚙️ AGENT_LOGIC
**Focus**: Business Logic, State, & Algorithms.
- **Contract**: Accepts feature requirements; Outputs modular, testable Javascript/Python functions.
- **Rule**: Focus on edge case handling and data transformation integrity.

## 💾 AGENT_DATA
**Focus**: Schemas & Persistence.
- **Contract**: Accepts data models; Outputs SQL/Prisma schemas and migration scripts.
- **Rule**: Implement RBAC fields (`created_by`, `role_required`) in every table from Day 1.

## 📡 AGENT_API
**Focus**: Endpoints & Connectivity.
- **Contract**: Accepts logic definitions; Outputs REST/GraphQL endpoints with Swagger/OpenAPI docs.
- **Rule**: All endpoints must require authentication headers.

## 🛡️ AGENT_AUTH
**Focus**: Identity & Security.
- **Contract**: Accepts user credentials/tokens; Outputs JWT sessions and role validation middleware.
- **Rule**: Implement "Least Privilege" access by default.

## 🧪 AGENT_TEST
**Focus**: Quality Assurance.
- **Contract**: Accepts code snippets; Outputs test suites (Unit/E2E) and pass/fail reports.
- **Rule**: Critical paths must maintain 100% test coverage.

## 🔍 AGENT_REVIEW
**Focus**: Governance & Compliance.
- **Contract**: Accepts pull requests/code blocks; Outputs feedback on performance, security, and readability.
- **Rule**: Reject any code that bypasses the security layer or uses placeholders.

---
> **Version**: 1.0 (Single-User Power Environment)
