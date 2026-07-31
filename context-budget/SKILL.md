---
name: context-budget
description: Optimizes Claude Code context window usage — runs an inventory, detects issues, and outputs a prioritized savings report. Assumes a 200K context window unless the user specifies otherwise.
version: "1.0.0"
author: "mykcs"
license: "MIT"
last_updated: "2026-07-19"
triggers:
  - context-budget
  - /context-budget
  - optimize context
  - context window
  - /context
  - 上下文优化
  - context truncation
when_to_use: |
  context budget fix / context 重 / /context
---

# context-budget

> Migrated from `~/.claude/commands/context-budget.md` on 2026-06-15.
> Original slash command continues to work; this skill version supports auto-trigger by description keyword.

Use this only if you still invoke `/context-budget`. The maintained workflow lives in `skills/context-budget/SKILL.md`.

## Canonical Surface

- Prefer the `context-budget` skill directly.
- Keep this file only as a compatibility entry point.

## Arguments

$ARGUMENTS

## Delegation

Apply the `context-budget` skill.
- Pass through `--verbose` if the user supplied it.
- Assume a 200K context window unless the user specified otherwise.
- Return the skill's inventory, issue detection, and prioritized savings report without re-implementing the scan here.

