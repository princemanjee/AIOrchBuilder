---
description: 
---

## ITERATIVE_PROCESS
**Mandatory Self-Correction Cycle (Before ANY Final Output):**

```
┌─────────────────────────────────────────────────────────┐
│                    DRAFT PHASE                          │
│  Generate initial solution based on requirements        │
└─────────────────────┬───────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────┐
│                   CRITIQUE PHASE                        │
│  Self-evaluate against these dimensions:                │
│  □ Functional Correctness: Does it work as intended?    │
│  □ Requirement Alignment: Does it match what was asked? │
│  □ Code Quality: Is it clean, readable, maintainable?   │
│  □ Edge Cases: Are boundaries and errors handled?       │
│  □ Security: Are there vulnerabilities?                 │
│  □ Performance: Are there obvious inefficiencies?       │
└─────────────────────┬───────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────┐
│                   REFINE PHASE                          │
│  Address ALL issues identified in Critique Phase        │
│  Document what changed and why                          │
└─────────────────────┬───────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────┐
│                   VERIFY PHASE                          │
│  Run refined solution through Critique checklist again  │
│  If pass → Output; If fail → Return to Refine Phase     │
└─────────────────────────────────────────────────────────┘
```

**Iteration Tracking Format:**
```
=== ITERATION LOG ===
Version: v{X.X}
Changes from Previous:
  - [ADDED]: ...
  - [MODIFIED]: ...
  - [REMOVED]: ...
  - [FIXED]: ...
Feedback Addressed:
  - Issue #1: [description] → [resolution]
  - Issue #2: [description] → [resolution]
Remaining Issues: [count] ([severities])
Next Steps: ...
=====================
```

---