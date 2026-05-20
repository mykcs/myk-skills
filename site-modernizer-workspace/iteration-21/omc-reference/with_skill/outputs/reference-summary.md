# OMC Executor Agent Reference Summary

## Role

The `executor` agent (model: sonnet) is responsible for **implementation and refactoring** tasks in the OMC agent orchestration system. It receives detailed plans from `planner` or `architect` agents and executes code changes, working directly with the codebase to transform specifications into working code.

## Typical Use Cases

- Executing multi-file code changes based on approved plans
- Refactoring existing codebases while preserving behavior
- Implementing features from design specifications
- Applying planned modifications across the project

## Available Tools

The executor has access to standard Code Intelligence tools (LSP, AST grep/replace), Utility tools (python_repl), and standard file operations (Read, Edit, Write, Bash). It can also be invoked via team orchestration: `/team N:executor "task"`.

## Invocation

Via OMC team pipeline: `team-exec` stage delegates to executor agents in parallel lanes. Direct invocation: `/team N:executor "task description"`.