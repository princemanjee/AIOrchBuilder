---
trigger: always_on
---

## TOOL_INTEGRATION
**Available Tools & When to Use Them:**

| Tool | Trigger Condition | Usage Protocol |
|------|------------------|----------------|
| **Code Interpreter** | Any code generation, testing, or debugging | Execute code to validate functionality; capture stdout/stderr |
| **File System** | Multi-file projects, asset management | Create project structure; organize by agent responsibility |
| **Search/RAG** | Unknown frameworks, APIs, best practices | Query before implementing unfamiliar technologies |
| **Memory/Context Store** | Cross-iteration persistence | Store: requirements, decisions, feedback history, version states |

**Tool Invocation Pattern:**
```
{TOOL_CALL: [tool_name]}
    Purpose: [why this tool is needed]
    Input: [what is being passed]
    Expected Output: [what success looks like]
{/TOOL_CALL}
```

---