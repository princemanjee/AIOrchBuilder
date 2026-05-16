---
trigger: always_on
---

## OUTPUT_FORMAT
**Structure ALL Responses Using This Format:**

```markdown
# 🎯 PHASE: [Current Phase Name]
## Status: [In Progress | Complete | Blocked]

---

## 📋 Summary
[2-3 sentence overview of what this output contains]

---

## 📄 Deliverable: [DOCUMENT_NAME]

[Structured content based on phase - see phase-specific formats below]

---

## 🔧 Artifacts Generated

| File/Component | Type | Status |
|---------------|------|--------|
| ... | ... | ... |

---

## 📊 Metrics Snapshot

- Requirements Covered: X/Y (Z%)
- Tests Passing: A/B (C%)
- Open Issues: D (E critical, F high)

---

## ➡️ Next Steps

1. [Immediate next action]
2. [Following action]

---

## ❓ Questions/Decisions Needed (if any)

- [ ] Question 1?
- [ ] Question 2?
```

**Code Block Requirements:**
- Language-tagged (```python, ```javascript, etc.)
- Include file path as first comment: `# File: src/components/TaskList.jsx`
- Runnable without modification (no placeholders like `...` unless explicitly prototyping)

---
