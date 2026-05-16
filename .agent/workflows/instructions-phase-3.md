---
description: 
---

# ONLY EXECUTE THESE INSTRUCTIONS IF PHASE 2 HAS BEEN COMPLETED

## INSTRUCTIONS
Execute the following phases sequentially. Each phase must complete before the next begins.

### PHASE 3: AGENT CONSTRUCTION & DELEGATION
Spawn the following specialized agents (or subset based on app complexity):

| Agent ID | Responsibility | Inputs | Outputs |
|----------|---------------|--------|---------|
| `AGENT_UI` | Frontend/Interface Development | Blueprint, UI requirements | UI components, views |
| `AGENT_LOGIC` | Business Logic & Core Functions | Blueprint, feature specs | Core modules, algorithms |
| `AGENT_DATA` | Database & Data Layer | Entity definitions | Schema, queries, ORM |
| `AGENT_API` | API/Integration Layer | Endpoints spec | Routes, controllers |
| `AGENT_AUTH` | Authentication & Security | Auth requirements | Auth flow, middleware |
| `AGENT_TEST` | Testing & Validation | All code outputs | Test suites, reports |
| `AGENT_REVIEW` | Code Review & Feedback | All code outputs | Improvement suggestions |

3.1. **Activate Required Agents**: Based on app scope.
3.2. **Define Inter-Agent Contracts**: API signatures between components.
3.3. **Establish Build Order**: Dependency-aware sequencing.
3.4. **Output**: `AGENT_MANIFEST` with responsibilities and interfaces.

---