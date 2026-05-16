---
trigger: always_on
---

## CONSTRAINTS

### DOS
- **DO** explicitly parse and confirm requirements before building.
- **DO** decompose the app into discrete, agent-assignable components.
- **DO** generate working, executable code (not pseudocode) unless prototyping.
- **DO** include error handling, input validation, and edge case management.
- **DO** run all code through testing agents before presenting as complete.
- **DO** document all architectural decisions and trade-offs.
- **DO** version each iteration clearly (v1.0, v1.1, v2.0, etc.).
- **DO** provide actionable feedback after each test cycle.
- **DO** ask clarifying questions when requirements have critical ambiguities.

### DONTS
- **DON'T** assume missing requirements; flag them explicitly.
- **DON'T** skip the testing phase under any circumstances.
- **DON'T** present untested code as "complete."
- **DON'T** hard-code values that should be configurable.
- **DON'T** ignore security considerations (sanitization, auth, etc.).
- **DON'T** proceed to the next iteration without summarizing changes from feedback.
- **DON'T** create monolithic code; maintain modular, agent-aligned architecture.
- **DON'T** abandon previous context between iterations.

---