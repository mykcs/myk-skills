---
name: site-modernizer-workspace
description: Working directory for site modernization iterations
metadata:
  type: workspace
disable-model-invocation: true
---

# Site Modernizer Workspace

Active workspace for site modernization iterations (1-19).
No standalone skill — used internally by the modernization workflow.

## Garbage Cleanup Rule

**After each benchmark iteration completes, immediately clean up:**

- `*/mock-repo/` directories (cloned test repos, rebuildable)
- `*/outputs/dist/` directories (build artifacts, rebuildable)
- `*/node_modules/` within mock repos

**Command:**
```bash
find . -type d -name "mock-repo" -exec rm -rf {} + 2>/dev/null
find . -type d -path "*/outputs/dist" -exec rm -rf {} + 2>/dev/null
```

**Why:** Unchecked benchmark artifacts accumulate across iterations (21 iterations × multiple benchmarks = 12GB+). Cleanup must be immediate, not deferred.
