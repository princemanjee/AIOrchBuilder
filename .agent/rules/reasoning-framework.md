---
trigger: always_on
---

## REASONING_FRAMEWORK
**Chain of Thought (CoT) Protocol:**

Before generating ANY code or making architectural decisions, execute internal reasoning:

```
[REASONING_START]

  1. UNDERSTAND: What exactly is being asked? Restate in my own words.
  2. DECOMPOSE: What are the sub-problems? List them.
  3. ANALYZE: What are the options for each sub-problem? (Min 2 alternatives)
  4. EVALUATE: What are the trade-offs? Score each option.
  5. DECIDE: Which option wins and why?
  6. VALIDATE: Does this decision align with requirements and constraints?

[REASONING_END]
```

**Tree of Thought (ToT) for Complex Decisions:**

When facing architectural choices with significant downstream impact:

```
[BRANCH_EXPLORATION]

  Branch A: [Option 1]
    → Pro: ...
    → Con: ...
    → Downstream Impact: ...

  Branch B: [Option 2]
    → Pro: ...
    → Con: ...
    → Downstream Impact: ...

  Branch C: [Option 3]
    → Pro: ...
    → Con: ...
    → Downstream Impact: ...

  [SELECTED_BRANCH]: [Winner] because [justification]

[/BRANCH_EXPLORATION]
```

**Silent Reasoning Directive:**
Execute CoT/ToT internally. Only surface reasoning when:
- User explicitly requests explanation
- Decision has major trade-offs user should approve
- Ambiguity requires user input

---