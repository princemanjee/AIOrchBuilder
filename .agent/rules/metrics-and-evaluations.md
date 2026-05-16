---
trigger: always_on
---

## METRICS_AND_EVALUATION
**Quality Gates (Must Pass Before Delivery):**

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Functional Completeness | 100% of stated requirements | Requirement traceability matrix |
| Test Pass Rate | ≥ 95% (100% for critical paths) | Automated test execution |
| Code Syntax Validity | 0 syntax errors | Linter/Interpreter execution |
| Runtime Errors | 0 uncaught exceptions | Test suite + manual runs |
| Security Baseline | No critical vulnerabilities | OWASP checklist review |
| Code Readability | Consistent naming, comments on complex logic | Self-review checklist |
| Modularity Score | Each agent's code independently testable | Dependency analysis |

**Iteration Exit Criteria:**

```
EXIT_CONDITION = (
  (test_pass_rate >= 0.95) AND
  (critical_issues == 0) AND
  (high_issues == 0) AND
  (user_approved OR iteration_count >= MAX_ITERATIONS)
)
```

**Feedback Severity Definitions:**
- **CRITICAL**: App crashes, data loss, security breach → Must fix before any delivery
- **HIGH**: Feature broken, major UX issue → Must fix before version release
- **MEDIUM**: Feature works incorrectly in edge case → Should fix this iteration
- **LOW**: Cosmetic, minor improvement → Can defer to next iteration

---