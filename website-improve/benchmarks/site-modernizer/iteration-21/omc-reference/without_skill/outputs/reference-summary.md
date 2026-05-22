# OMC Agent Reference: Executor

## Role

The **executor** agent is the code implementation unit in OMC's multi-agent pipeline, receiving structured plans from the **planner** agent and producing verified code changes. It sits between the planning phase and verification phase, translating architectural decisions into working code.

## Tools

Executor agents have full access to all Claude Code tools (Read, Edit, Write, Bash) for file operations and command execution, with **model routing to `opus`** for complex multi-file changes as specified in MEMORY.md delegation rules.

## Typical Use Cases

Executor is invoked via the `executor` keyword trigger in the OMC team pipeline. The canonical flow is `planner → executor → security-reviewer → verify → push` (per CASE-010 design migration case), where executor handles the heavy lifting of actual code modifications after the planner has defined the approach. For complex multi-file refactors, the executor works in conjunction with the code-reviewer agent for review passes exceeding 3 files.